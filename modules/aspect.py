from itertools import product

from modules.dependencies import *
from modules.environment import Environment
from modules.sentiment import *
from modules.wordnetdic import WordnetDictionary

environment = Environment()
sentimentDic = SentimentDictionary()
wordnetdic = WordnetDictionary()

class Aspect:
        def __init__(self):
                self.categories = environment.get_aspect_categories()
                self.categorysynsets = wordnetdic.getSynsets(self.categories)
                self.minSimilarityScore = 0.7

        def wordHasSentiment(self, word):
	        return sentimentDic.wordInDictionary(word['word'], word['pos_tag'])

        def isAspect(self, synset):
                for categorysynset in self.categorysynsets:
                        vals = [val if val else 0 for val in [wordnetdic.getWupSimilarity(s1,s2) for s1,s2 in product(synset,categorysynset)]]
                        if(len(vals)>0):
                                catescore = max(vals)
                        else:
                                catescore = 0
                        if catescore > self.minSimilarityScore:
                                return True
                return False

        def getAspectCategory(self, aspect):
                temp = []
                synsets1 = wordnetdic.getSynset(aspect)
                for (i,category) in enumerate(self.categories):
                        synsets2 = self.categorysynsets[i]
                        for s1,s2 in product(synsets1,synsets2):
                                score = wordnetdic.getWupSimilarity(s1,s2)
                                temp.append((score,category))
                temp = sorted(temp, key=lambda x: (x[0] is not None, x[0]), reverse=True)
                if len(temp)>1 and temp[0][0] and temp[0][0] > self.minSimilarityScore:
                        return temp[0][1]
                return None
        
        def getAspectClusters(self, aspectlist):
                aspectsynsets = wordnetdic.getSynsets(aspectlist)
                removeindex = 0
                for aspect in aspectlist:
                        if not self.isAspect(aspectsynsets[removeindex]):
                                del aspectlist[removeindex]
                                del aspectsynsets[removeindex]
                                removeindex -= 1
                        removeindex += 1
                aspectgroup = {}
                for (i,a1) in enumerate(aspectlist):
                        aspectgroup[a1] = {'group':a1, 'score':0}
                        synsets1 = aspectsynsets[i]
                        for (j,a2) in enumerate(aspectlist):
                                if a1 != a2:
                                        synsets2 = aspectsynsets[j]
                                        vals = [val if val else 0 for val in [wordnetdic.getWupSimilarity(s1,s2) for s1,s2 in product(synsets1,synsets2)]]
                                        if(len(vals)>0):
                                                maxscore = max(vals)
                                                if aspectgroup[a1]['score'] < maxscore:
                                                        aspectgroup[a1]['score'] = maxscore
                                                        aspectgroup[a1]['group'] = a2
                return aspectgroup

        def categorizeAspects(self, aspects):
                categories = {}
                for aspect, polarity in aspects.items():
                        if aspect != "hashtags":
                                category = self.getAspectCategory(aspect)
                                if category:
                                        if category not in categories:
                                                categories[category] = {}
                                        categories[category][aspect] = polarity
                        else:
                                categories["hashtags"] = polarity
                return categories


        def clusterAspects(self, aspects):
                categories = {}
                if "hashtags" in aspects:
                        categories["hashtags"] = aspects["hashtags"]
                        del aspects["hashtags"]
                aspectlist = [aspect for aspect in aspects if aspect != "hashtags"]
                if len(aspectlist)==0:
                        return categories
                if len(aspectlist)==1:
                        categories[aspectlist[0]] = aspects 
                        return categories
                aspectgroup = self.getAspectClusters(aspectlist)
                def createGroup(key):
                        del aspectgroup[key]
                        items = []
                        for key1,value1 in aspectgroup.items():
                                if key == value1['group']:
                                        items.append(key1)
                        for item in items:
                                items = items + createGroup(item)
                        return items
                for aspect in aspectlist:
                        if aspect in aspectgroup:
                                categories[aspect] = {aspect: aspects[aspect]}
                                for aspectword in createGroup(aspect):
                                        categories[aspect][aspectword] = aspects[aspectword]
                return categories

        def getWordScore(self, word, postag):
                return sentimentDic.getSentimentScore(word, postag)

        def addModsToOpinion(self, words, opinionwords, word):
                mods = getAdvmodorAmod(words, word)
                for mod in mods:
                        opinionwords.append({"word":mod, "pos_tag":words[mod]["pos_tag"]})

        def addConjsToOpinion(self, words, opinionwords, word):
                conjs = getConjs(words, word)
                for conj in conjs:
                        opinionwords.append({"word":conj, "pos_tag":words[conj]["pos_tag"]})

        def addItem(self, words, opinionwords, opinionword):
                if isNeg(words, opinionword['word']):
                        opinionword['neg'] = True
                opinionwords.append(opinionword)
                self.addConjsToOpinion(words, opinionwords, opinionword['word'])
                self.addModsToOpinion(words, opinionwords, opinionword['word'])
        
        def getExAsScore(self, words, aspect):
                score = 0.0
                opinionwords = []
                for key in words.keys():
                        if "ccomp" in words[key]: # if the key has a clasual complement and a nominal subject
                                ccomp = words[key]["ccomp"]
                                if self.wordHasSentiment({"word":ccomp, "pos_tag":words[ccomp]["pos_tag"]}): # if the comlement has a sentiment
                                        if "nsubj" in words[key]:
                                                aspectword = words[key]["nsubj"]
                                        else:
                                                aspectword = key
                                        if aspectword == aspect:
                                                self.addItem(words, opinionwords, {"word":ccomp, "pos_tag":words[ccomp]["pos_tag"]})
                        if "xcomp" in words[key]: # if the key has a open clasual complement and a nominal subject
                                xcomp = words[key]["xcomp"]
                                if self.wordHasSentiment({"word":xcomp, "pos_tag":words[xcomp]["pos_tag"]}): # if the comlement has a sentiment
                                        if "nsubj" in words[key]:
                                                aspectword = words[key]["nsubj"]
                                        else:
                                                aspectword = key
                                        if aspectword == aspect:
                                                self.addItem(words, opinionwords, {"word":xcomp, "pos_tag":words[xcomp]["pos_tag"]})
                        if "advmod" in words[key]: # if key has a adverbial modifier
                                advmod = words[key]["advmod"]
                                if "nmod" in words[key]: # if the key has a nominal modifier
                                        aspectword = words[key]["nmod"]
                                else:
                                        aspectword = getNMod(words[key]) # if the key has a nominal modifier
                                if not aspectword:
                                        if "dobj" in words[key]: # if key has direct object
                                                dboj = words[key]["dobj"]
                                                if "nmod" in words[dboj]: # if the objet has a nominal modifier
                                                        aspectword = words[dboj]["nmod"]
                                                else:
                                                        aspectword = getNMod(words[dboj]) # if the objet has a nominal modifier
                                                if not aspectword:
                                                        if "nsubj" in words[dboj]: # if the objet has a nominal subject
                                                                aspectword = words[dboj]["nsubj"]
                                                        else:
                                                                aspectword = dboj
                                        else: # if key does not have a direct object
                                                aspectword = key
                                if aspectword == aspect:
                                        if self.wordHasSentiment({"word":advmod, "pos_tag":words[advmod]["pos_tag"]}): # if adverb has a sentiment
                                                self.addItem(words, opinionwords, {"word":advmod, "pos_tag":words[advmod]["pos_tag"]})
                                        elif self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if verb has a sentiment
                                                self.addItem(words, opinionwords, {"word":key, "pos_tag":words[key]["pos_tag"]})
                        if "amod" in words[key]: # if key has a adjecttival modifier
                                amod = words[key]["amod"]
                                if key == aspect and self.wordHasSentiment({"word":amod, "pos_tag":words[amod]["pos_tag"]}): # if adjective has a sentiment
                                        self.addItem(words, opinionwords, {"word":amod, "pos_tag":words[amod]["pos_tag"]})
                        if ("cop" in words[key] or "aux" in words[key]) and self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): #if key has copular verb relationship with a term and key has a sentiment
                                if "nmod" in words[key]: # if the key has a nominal modifier
                                        aspectword = words[key]["nmod"]
                                else:
                                        aspectword = getNMod(words[key]) # if the key has a nominal modifier
                                if not aspectword:
                                        if "nsubj" in words[key]: # if the key has a nominal subject
                                                aspectword = words[key]["nsubj"]
                                if aspectword and aspectword == aspect:
                                        self.addItem(words, opinionwords, {"word":key, "pos_tag":words[key]["pos_tag"]})


                        # if ("ccomp" in words[key] or "xcomp" in words[key]) and self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the key has open or clausal complement and key has sentiment
                        #         relations = []
                        #         if "ccomp" in words[key]:
                        #                 relations.append(words[key]["ccomp"])
                        #         if "xcomp" in words[key]:
                        #                 relations.append(words[key]["xcomp"])
                        #         for relation in relations:
                        #                 complement = relation
                        #                 complements = [complement]
                        #                 if complement == aspect:
                        #                         opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        #                 while "conj" in words[complement] and complement not in complements:
                        #                         complement = words[complement]["conj"]
                        #                         complements.append(complement)
                        #                         if complement == aspect:
                        #                                 opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        # if "dobj" in words[key] and self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the key has direct object relation and key has sentiment
                        #         term = words[key]["dobj"]
                        #         if term == aspect:
                        #                 opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        #         if "nmod" in words[term] and words[term]["nmod"] == aspect:
                        #                 opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        # if "advcl" in words[key]: # if the key has adverbial clause modifier
                        #         term = words[key]["advcl"]
                        #         if self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the verb has a sentiment
                        #                 if term == aspect:
                        #                         opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        #                 if "nmod" in words[term] and words[term]["nmod"] == aspect:
                        #                         opinionwords.append({"word":key, "pos_tag":words[key]["pos_tag"]})
                        #         if self.wordHasSentiment({"word":term, "pos_tag":words[term]["pos_tag"]}): # if the advcl has a sentiment
                        #                 if key == aspect:
                        #                         opinionwords.append({"word":term, "pos_tag":words[term]["pos_tag"]})
                        #                 if "nmod" in words[key] and words[key]["nmod"] == aspect:
                        #                         opinionwords.append({"word":term, "pos_tag":words[term]["pos_tag"]})
		
                for word in opinionwords:
                        wordscore = self.getWordScore(word['word'], word['pos_tag'])
                        if 'neg' in word and word['neg']:
                                wordscore *= -1
                        score += wordscore
                return (score/len(opinionwords)) if (len(opinionwords)>0) else 0.0

        def getAspectScores(self, tweets):
                opinion = {}
                for tweet in tweets:
                        implicit_aspects = []
                        explicit_aspects = []
                        if "implicit_aspects" in tweet: implicit_aspects = tweet["implicit_aspects"]
                        if "explicit_aspects" in tweet: explicit_aspects = tweet["explicit_aspects"]
                        for idx,sentence in enumerate(tweet["parse"]):
                                if len(explicit_aspects) > idx:
                                        for aspect in explicit_aspects[idx]:
                                                if aspect not in opinion:
                                                        opinion[aspect] = {"count":0,"score":0.0}  
                                                opinion[aspect]["score"] += self.getExAsScore(sentence, aspect)
                                                opinion[aspect]["count"] += 1
                                if len(implicit_aspects) > idx:
                                        for aspect, opinionwords in implicit_aspects[idx].items():
                                                if aspect not in opinion:
                                                        opinion[aspect] = {"count":0,"score":0.0}
                                                for opinionword in opinionwords:
                                                        wordscore = self.getWordScore(opinionword["word"], opinionword["pos_tag"])
                                                        if "neg" in opinionword and opinionword["neg"]:
                                                                wordscore *= -1
                                                        opinion[aspect]["score"] += wordscore
                                                opinion[aspect]["score"] = (opinion[aspect]["score"]/len(opinionwords)) if (len(opinionwords)>0) else 0.0
                                                opinion[aspect]["count"] += 1
                        # hashtagcount = 0
                        # hashtahscore = 0.0
                        # for hashtag in tweet["hashtags"]:
                        #         score = sentimentDic.getHashtagSentimentScore(hashtag["text"])
                        #         if score:
                        #                 hashtahscore += score
                        #                 hashtagcount += 1
                        # if hashtagcount > 0:
                        #         if "hashtags" not in opinion:
                        #                 opinion["hashtags"] = {"count":0,"score":0.0}                
                        #         opinion["hashtags"]["score"] = hashtahscore/hashtagcount
                        #         opinion["hashtags"]["count"] += 1
                polarities = {}
                for aspect,item in opinion.items():
                        polarities[aspect] = item["score"]/item["count"]
                return polarities