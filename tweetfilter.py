import glob,os,json
from nltk.corpus import wordnet as wn
from multiprocessing.pool import ThreadPool
from datetime import datetime

from modules.processtring import *
from modules.environment import Environment
from modules.sentiment import *
from modules.dependencyparser import *
from modules.geolocations import *

class TweetFilter:
    def __init__(self):
        self.environment = Environment()
        self.new_datapath = self.environment.get_new_datapath()
        self.old_datapath = self.environment.get_old_datapath()
        self.filtered_datapath = self.environment.get_filtered_datapath()
        self.cache = self.environment.get_cache()
        self.pool = ThreadPool(processes=2)
        self.sentimentDic = SentimentDictionary()
        self.keywords = self.environment.get_keywords()

    def isSubjective(self, text, hashtags):
        tokens = getKeywords(text)
        tokens += hashtags
        for token in tokens:
            syn_sets = wn.synsets(token)
            for syn_set in syn_sets:
                for syn in syn_set.lemma_names():
                    if syn in self.keywords:
                        return True
        return False

    def generateParseResults(self, sentences):
        sentencewords = []
        for sentence in sentences['sentences']:
            words={}
            for wl in sentence['words']:
                innerd={}
                innerd['pos_tag']=wl[1]['pos']
                innerd['lemma']=wl[1]['lemma'].lower()
                innerd['ner']=wl[1]['ner']
                for depl in sentence['dependencies']['basic-dependencies']:
                    if depl[1]==wl[0]:
                        innerd[depl[0]]=depl[2].lower()
                words[wl[0].lower()]=innerd
            sentencewords.append(words)
        return sentencewords

    def generateTweetObject(self, cur_item, text, sentiment_text):
        emoticons = extractEmoticons(text)
        parseres = []
        if(sentiment_text.strip() != ""):
            sentences = parse(sentiment_text)
            parseres = self.generateParseResults(sentences)
        hasopinion = []
        for sentence in parseres:
            hasopinion.append(self.sentimentDic.hasSentiment([{'word': word, 'pos_tag': ele['pos_tag']}
            for word, ele in sentence.items()]))
        tweet = {
            'id' : cur_item["id"],
            'datetime' : cur_item["created_at"],
            'text' : text,
            'user_id' : cur_item["user"]["id"],
            'user_location_str' : cur_item["user"]["location"], 
            'location' : cur_item["geo"],
            'hashtags': cur_item["entities"]["hashtags"],
            'sentiment_text': sentiment_text.lower(),
            'parse': parseres,
            'emoticons': emoticons,
            'opinionate': hasopinion
        }
        return tweet

    def isExist(self, tweetArr, text):
        if text in [tweet["text"] for tweet in tweetArr]:
            return True
        return False

    def verifyLocation(self, entities, hashtags, coordinates):
        for entity in entities:
            if isLocationInArea(entity, coordinates):
                return True
        for hashtag in hashtags:
            try:
                for entity in camelCaseSplit(hashtag['text']):
                    if isLocationInArea(entity, coordinates):
                        return True
            except:
                continue
        return False

    def tVerifyLocationfunc(self, entities, hashtags, location):
        return self.verifyLocation(entities,hashtags,location)

    def tGetCensusTractfunc(self, latitude, longitude):
        returnval = getCensusTract(latitude, longitude)
        if returnval:
            (postal,city,country) = returnval
            return postal+"_"+city+"_"+country
        else:
            return None

    def verifyLocationAndGetCensustract(self, entities, hashtags, latitude, longitude):
        #locationVarified = self.pool.apply_async(self.tVerifyLocationfunc, (entities,hashtags,(latitude,longitude))).get()
        locationVarified = True
        postalkey = self.pool.apply_async(self.tGetCensusTractfunc, (latitude,longitude)).get()
        return (locationVarified, postalkey)

    def isTourist(self, tweets):
        date_year = {}
        for tweet in tweets:
            tweetlocation = tweet['location']
            userlocationstr = tweet['user_location_str']
            if isLocationCloser(userlocationstr, (tweetlocation["coordinates"][0],tweetlocation["coordinates"][1]), 50):
                return False
            curdate = datetime.strptime(tweet["datetime"],"%a %b %d %H:%M:%S +0000 %Y")
            if curdate.year not in date_year:
                date_year[curdate.year] = []
            date_year[curdate.year].append(curdate)
        for year, dates in date_year.items():
            dates.sort()
            first_date = dates[0]
            last_date = dates[-1]
            diff = last_date-first_date
            if diff.days > 30*2 and diff.days < 365:
                return False
        return True

    def genarateJson(self, tweets_file):
        loader = ['-','\\','|','/']
        i = 0
        count = 0
        cache = self.environment.get_cache()
        for line in tweets_file:
            try:
                cur_item = json.loads(line)
                geotag = cur_item["geo"]
                if not geotag:
                    continue
                b = "Loading  tweets ("+str(count)+"/"+str(i)+")   "+loader[i%4]
                print (b, end="\r")
                i = i+1
            except:
                continue
            if "extended_tweet" in cur_item:
                text = clearText(cur_item["extended_tweet"]["full_text"])
                hashtags = [ele["text"] for ele in cur_item["extended_tweet"]["entities"]["hashtags"]]
            else:
                text = clearText(cur_item["text"])
                hashtags = [ele["text"] for ele in cur_item["entities"]["hashtags"]]
            latitude = geotag["coordinates"][0]
            longitude = geotag["coordinates"][1]    
            sentiment_text = getSentimentText(text)
            entities = getEntities(sentiment_text)
            if self.isSubjective(sentiment_text, hashtags):
                (locationVarified, key) = self.verifyLocationAndGetCensustract(entities, hashtags, latitude, longitude)
                if not (locationVarified and key):
                    continue
                curArr = {}
                filepath = self.filtered_datapath+key+".json"
                try:
                    data_file = open(filepath, "r", encoding='utf8')
                    curArr = json.loads(data_file.read())
                    data_file.close()
                except:
                    pass
                user_id = str(cur_item["user"]["id"])
                if user_id not in curArr:
                    curArr[user_id] = []
                if not self.isExist(curArr[user_id], text):
                    tweetObj = self.generateTweetObject(cur_item, text, sentiment_text)
                    curArr[user_id].append(tweetObj)
                    count = count+1
                    if not self.isTourist(curArr[user_id]):
                        del curArr[user_id]
                        count = count-1
                    with open(filepath, 'w', encoding='utf8') as outfile:
                        json.dump(curArr, outfile)
                        outfile.close()
                    for array in cache["new_filtered_data"]:
                        if key not in array:
                            array.append(key)
        self.environment.set_cache(cache)
                            
    def readTweets(self):
        for filename in glob.glob(self.new_datapath + '*.txt'):
            tweets_file = open(filename, 'r', encoding='utf8', errors='ignore')
            self.genarateJson(tweets_file)
            os.rename(filename, self.old_datapath + filename.split('/')[-1])
            tweets_file.close()