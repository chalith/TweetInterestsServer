from nltk.corpus import wordnet as wn

class WordnetDictionary():
    def getSynsets(self, itemlist):
        synsetsarray = []
        for item in itemlist:
            synsets=wn.synsets(item)
            synsetsarray.append(synsets)
        return synsetsarray

    def getSynset(self, term):
        return wn.synsets(term)

    def getWupSimilarity(self, s1,s2):
        return wn.wup_similarity(s1,s2)