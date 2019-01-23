import pickle
import nltk

from nltk.stem.wordnet import WordNetLemmatizer
from spacy.lang.en import English
from nltk.corpus import sentiwordnet as swn

en_stop = set(nltk.corpus.stopwords.words('english'))
parser = English()

class SentimentDictionary:
    def wordInDictionary(self, word, pos):
        if self.getSentimentScore(word, pos) != None:
            return True
        return False

    def hasSentiment(self, tokens):
        for token in tokens:
            if self.wordInDictionary(token['word'], token['pos_tag']):
                return True
        return False

    def getSentimentScore(self, word, pos):
        score = 0.0
        objscore = 0.0
        tag = ''
        if pos.startswith('NN'):
            tag = 'n'
        elif pos.startswith('JJ'):
            tag = 'a'
        elif pos.startswith('V'):
            tag = 'v'
        elif pos.startswith('R'):
            tag = 'r'
        else:
            tag = ''
        if (tag != ''):
            synsets = list(swn.senti_synsets(word, tag))
            if (len(synsets) > 0):
                for syn in synsets:
                    score += syn.pos_score() - syn.neg_score()
                    objscore += syn.obj_score()
                score = score / len(synsets)
                objscore = objscore / len(synsets)
            else:
                return None
        else:
            return None
        return (score if objscore != 1.0 else None)

    def getHashtagSentimentScore(self, word):
        score = 0.0
        objscore = 0.0
        synsets = list(swn.senti_synsets(word))
        if (len(synsets) > 0):
            for syn in synsets:
                score += syn.pos_score() - syn.neg_score()
                objscore += syn.obj_score()
            score = score / len(synsets)
            objscore = objscore / len(synsets)
        else:
            return None
        return (score if objscore != 1.0 else None)