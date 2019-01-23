import json,pickle
import numpy as np
import sklearn.cluster
import distance

from datetime import datetime
from efficient_apriori import apriori
from modules.dependencies import *
from modules.sentiment import *
from modules.environment import Environment
from modules.aspect import *
environment = Environment()

class OpinionMiner:
    def __init__(self, censustract):
        self.sentimentDic = SentimentDictionary()
        self.censustract = censustract
        self.aspectObj = Aspect()
        self.census_tweets = {}
        self.months = environment.get_months()
        with open(environment.filtered_datapath+censustract+".json", 'r', encoding='utf8') as tweetfile:
            for user, tweets in json.loads(tweetfile.read()).items():
                for tweet in tweets:
                    #date = datetime.strptime(tweet["datetime"],"%a %b %d %H:%M:%S +0000 %Y")
                    #key = self.months[date.month-1]+"-"+str(date.year)
                    key = tweet["datetime"]
                    if key not in self.census_tweets:
                        self.census_tweets[key] = []
                    self.census_tweets[key].append(tweet)
            tweetfile.close()

    def getNountransaction(self, tweet):
        transactions = []
        for idx,sentence in enumerate(tweet.get('parse')):
            if bool(tweet["opinionate"][idx]):	
                transaction = []
                for word, elements in sentence.items():
                    if isNoun(sentence, word):
                        transaction.append(word)
                if(len(transaction)>0):
                    transactions.append(tuple(transaction))
        return transactions

    def getNountransactions(self, tweetArr):
        transactions = []
        for tweet in tweetArr:
            transaction = self.getNountransaction(tweet)
            transactions += transaction
        return transactions

    def wordHasSentiment(self, word):
	    return self.sentimentDic.wordInDictionary(word['word'], word['pos_tag'])

    def addItem(self, words, aspects, aspect, opinionword):
        if aspect in words:
            if isNeg(words, aspect):
                opinionword['neg'] = True
            if "compound" in words[aspect]:
                if isNeg(words, words[aspect]["compound"]):
                    opinionword['neg'] = True
                aspect = words[aspect]["compound"]+" "+aspect
        if aspect not in aspects:
            aspects[aspect] = []
        if isNeg(words, opinionword['word']):
            opinionword['neg'] = True
        aspects[aspect].append(opinionword)
        self.addConjs(words, aspects, aspect, opinionword['word'])
        self.addAdvnAmods(words, aspects, aspect, opinionword['word'])

    def addConjs(self, words, aspects, aspect, term):
        conjs = getConjs(words, term)
        for conj in conjs:
            if self.wordHasSentiment({"word":conj, "pos_tag":words[conj]["pos_tag"]}):
                opinionword = {"word":conj, "pos_tag":words[conj]["pos_tag"]}
                if isNeg(words, conj):
                    opinionword['neg'] = True
                aspects[aspect].append(opinionword)


    def addAdvnAmods(self, words, aspects, aspect, term):
        mods = getAdvmodorAmod(words, term)
        for mod in mods:
            if self.wordHasSentiment({"word":mod, "pos_tag":words[mod]["pos_tag"]}):
                opinionword = {"word":mod, "pos_tag":words[mod]["pos_tag"]}
                if isNeg(words, mod):
                    opinionword['neg'] = True
                aspects[aspect].append(opinionword)

    def implicitExtractor(self, words):
        aspects = {}
        for key in words.keys():
            if "xcomp" in words[key] or "ccomp" in words[key]: # if the key has a open clasual complement and a nominal subject
                if "xcomp" in words[key]:
                    comp = words[key]["xcomp"]
                else:
                    comp = words[key]["ccomp"]
                if self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the comlement has a sentiment
                    if "nmod" in words[comp]: # if the key has a nominal modifier
                        aspect = words[comp]["nmod"]
                    else:
                        aspect = getNMod(words[comp]) # if the key has a nominal modifier
                    if not aspect:
                        if "dobj" in words[comp]: # if key has direct object
                            dboj = words[comp]["dobj"]
                            if "nmod" in words[dboj]: # if the objet has a nominal modifier
                                aspect = words[dboj]["nmod"]
                            else:
                                aspect = getNMod(words[dboj]) # if the objet has a nominal modifier
                            if not aspect:
                                if "nsubj" in words[dboj]: # if the objet has a nominal subject
                                    aspect = words[dboj]["nsubj"]
                                else:
                                    aspect = dboj
                        else: # if key does not have a direct object
                            aspect = comp
                    if isNoun(words, aspect):
                        self.addItem(words, aspects, aspect, {"word":key, "pos_tag":words[key]["pos_tag"]})
            if "advmod" in words[key]: # if key has a adverbial modifier
                advmod = words[key]["advmod"]
                if "nmod" in words[key]: # if the key has a nominal modifier
                    aspect = words[key]["nmod"]
                else:
                    aspect = getNMod(words[key]) # if the key has a nominal modifier
                if not aspect:
                    if "dobj" in words[key]: # if key has direct object
                        dboj = words[key]["dobj"]
                        if "nmod" in words[dboj]: # if the objet has a nominal modifier
                            aspect = words[dboj]["nmod"]
                        else:
                            aspect = getNMod(words[dboj]) # if the objet has a nominal modifier
                        if not aspect:
                            if "nsubj" in words[dboj]: # if the objet has a nominal subject
                                aspect = words[dboj]["nsubj"]
                            else:
                                aspect = dboj
                    else: # if key does not have a direct object
                        aspect = key
                if isNoun(words, aspect):
                    if self.wordHasSentiment({"word":advmod, "pos_tag":words[advmod]["pos_tag"]}): # if adverb has a sentiment
                        self.addItem(words, aspects, aspect, {"word":advmod, "pos_tag":words[advmod]["pos_tag"]})
                    elif self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if verb has a sentiment
                        self.addItem(words, aspects, aspect, {"word":key, "pos_tag":words[key]["pos_tag"]})
            if "amod" in words[key]: # if key has a adjecttival modifier
                amod = words[key]["amod"]
                if isNoun(words, key) and self.wordHasSentiment({"word":amod, "pos_tag":words[amod]["pos_tag"]}): # if adjective has a sentiment
                    self.addItem(words, aspects, key, {"word":amod, "pos_tag":words[amod]["pos_tag"]})
            if ("cop" in words[key] or "aux" in words[key]) and self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): #if key has copular verb relationship with a term and key has a sentiment
                if "nmod" in words[key]: # if the key has a nominal modifier
                    aspect = words[key]["nmod"]
                else:
                    aspect = getNMod(words[key]) # if the key has a nominal modifier
                if not aspect:
                    if "nsubj" in words[key]: # if the key has a nominal subject
                        aspect = words[key]["nsubj"]
                if aspect and isNoun(words, aspect):
                    self.addItem(words, aspects, aspect, {"word":key, "pos_tag":words[key]["pos_tag"]})
                        

            # if ("ccomp" in words[key] or "xcomp" in words[key]): # if the key has open or clausal complement and comlement has sentiment
            #     if self.wordHasSentiment({"word":words[key]["ccomp"], "pos_tag":words[key]["pos_tag"]})
            #     if self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]})
            #     relations = []
            #     if "ccomp" in words[key]:
            #         relations.append(words[key]["ccomp"])
            #     if "xcomp" in words[key]:
            #         relations.append(words[key]["xcomp"])
            #     for relation in relations:
            #         complement = relation
            #         complements = [complement]
            #         if isVerb(words,complement):
            #             self.addItem(words, aspects, complement, {"word":key, "pos_tag":words[key]["pos_tag"]})
            #         if "nmod" in words[complement]:
            #             self.addItem(words, aspects, words[complement]["nmod"], {"word":key, "pos_tag":words[key]["pos_tag"]})
            #         while "conj" in words[complement] and complement not in complements: # if the complement has a conjunction
            #             complement = words[complement["conj"]]
            #             complements.append(complement)
            #             if isVerb(words,complement):
            #                 self.addItem(words, aspects, complement, {"word":key, "pos_tag":words[key]["pos_tag"]})
            #             if "nmod" in words[complement]:
            #                 self.addItem(words, aspects, words[complement]["nmod"], {"word":key, "pos_tag":words[key]["pos_tag"]})
            # if "dobj" in words[key] and self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the key has direct object relation and key has sentiment
            #     term = words[key]["dobj"]
            #     if isNoun(words, term):
            #         self.addItem(words, aspects, term, {"word":key, "pos_tag":words[key]["pos_tag"]})
            #     if "nmod" in words[term]:
            #         self.addItem(words, aspects, words[term]["nmod"], {"word":key, "pos_tag":words[key]["pos_tag"]})
            # if "advcl" in words[key]: # if the key has adverbial clause modifier
            #     term = words[key]["advcl"]
            #     if self.wordHasSentiment({"word":key, "pos_tag":words[key]["pos_tag"]}): # if the verb has a sentiment
            #         self.addItem(words, aspects, term, {"word":key, "pos_tag":words[key]["pos_tag"]})
            #         if "nmod" in words[term]:
            #             self.addItem(words, aspects, words[term]["nmod"], {"word":key, "pos_tag":words[key]["pos_tag"]})
            #     if self.wordHasSentiment({"word":term, "pos_tag":words[term]["pos_tag"]}): # if the advcl has a sentiment
            #         self.addItem(words, aspects, key, {"word":term, "pos_tag":words[term]["pos_tag"]})
            #         if "nmod" in words[key]:
            #             self.addItem(words, aspects, words[key]["nmod"], {"word":term, "pos_tag":words[term]["pos_tag"]})
        return aspects

    def extractImplicitAspects(self):
        for key,tweets in self.census_tweets.items():
            for tweet in tweets:
                tweet["implicit_aspects"]=[]
                for idx,words in enumerate(tweet["parse"]):
                    aspects = {}
                    if bool(tweet["opinionate"][idx]):
                        aspects=self.implicitExtractor(words)
                    tweet["implicit_aspects"].append(aspects)
        return self.census_tweets

    def extractExplicitAspects(self):
        for key,tweets in self.census_tweets.items():
            transactions = self.getNountransactions(tweets)
            if(len(transactions)>0):
                if len(tweets)>=5:
                    min_sup = 5/len(tweets)
                else:
                    min_sup = 0.2
                items,rules = apriori(transactions, min_support=min_sup,  min_confidence=1)
                for tweet in tweets:
                    tweet["explicit_aspects"]=[]
                    for idx,sentence in enumerate(tweet.get('parse')):
                        expasp = []
                        if bool(tweet["opinionate"][idx]):	
                            for size,itemsets in items.items():
                                for itemset,support in itemsets.items():
                                    for item in itemset:
                                        if item not in expasp and item in sentence:
                                            expasp.append(item)
                        tweet["explicit_aspects"].append(expasp)
        return self.census_tweets

    def getPolarities(self):
        self.extractImplicitAspects()
        #self.extractExplicitAspects()
        polarities = {}
        for key, tweets in self.census_tweets.items():
            polarities[key] = self.aspectObj.getAspectScores(tweets)
        if(len(self.census_tweets)>0):
            return polarities
        else:
            return False