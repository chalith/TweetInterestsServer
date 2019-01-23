import json,datetime
from dateutil.relativedelta import relativedelta
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from modules.environment import Environment
environment = Environment()
new_datapath = environment.get_new_datapath()

def filterTweet(tweet):
    if((tweet.get("retweeted_status"))
    or (tweet.get("in_reply_to_status_id"))
    or (tweet.get("in_reply_to_status_id_str"))
    or (tweet.get("in_reply_to_user_id"))
    or (tweet.get("in_reply_to_user_id_str"))
    or (tweet.get("in_reply_to_screen_name"))):
        return False
    return True

def getWords(data_arr):
    track = []
    for word in data_arr.get('without_stop'):
        if(word[0].strip()!=""):
            track.append(word[0])
    return track

class StdOutListener(StreamListener):
    def __init__(self, writeTweets):
        self.writeTweets = writeTweets
        self.tweets = []
        self.count = 0

    def on_data(self, data):
        if filterTweet(json.loads(data)):
            if self.count > environment.get_max_stream():
                return False
            self.tweets.append(json.loads(data))
            self.count = self.count + 1
            if len(self.tweets)>=10:
                self.writeTweets(self.tweets)
                print('%d tweets saved...\n' % self.count, end="\r")
                self.tweets = []
        return True
        
    def on_error(self, status):
        print(status)

def streamTweets():
    outputFile = open(new_datapath+datetime.datetime.now().strftime('%b_%d_%Y_%H%M%S')+".txt", "w", encoding='utf8')

    def writeTweets(tweets):
        for tweet in tweets:
            json.dump(tweet, outputFile)
            outputFile.write("\n")
        outputFile.flush()
    
    auth = OAuthHandler(environment.tweet_consumer_key, environment.tweet_consumer_secret)
    auth.set_access_token(environment.tweet_access_token, environment.tweet_access_token_secret)
    stream = Stream(auth, StdOutListener(writeTweets))
    stream.filter(track=environment.get_stream_filters(), 
        languages = ["en"])
    outputFile.close()