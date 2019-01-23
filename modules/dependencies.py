nouns = ["NN", "NNS", "NNP", "NNPS"]
verbs = ["VBD", "VB", "VBG", "VBN","VBP", "VBZ"]
adverbs =["RB", "RBR", "RBS"]
adjectives = ["JJ", "JJR", "JJS"]
wordattr = ['pos_tag','lemma','ner']

def getAdvmodorAmod(words, term):
	mods = []
	temp = term
	while "amod" in words[temp] and temp not in mods:
		temp = words[temp]["amod"]
		mods.append(temp)
	temp = term
	while "advmod" in words[temp] and temp not in mods:
		temp = words[temp]["advmod"]
		mods.append(temp)
	return mods


def getDirObjRel(words, term):
	if "dobj" in words[term]:
		return words[term]["dobj"]
	return None

def hasAuxiliary(words):
	for word in words.keys():
		if "aux" in words[word]:
			return True
	return False

def isNoun(words, term):
	if words[term]['pos_tag'] in nouns:
		return True
	return False

def isVerb(words, term):
	if words[term]['pos_tag'] in verbs:
		return True
	return False

def getNMod(items):
	for key,word in items.items():
		if key.startswith('nmod'):
			return word
	return None

def getConjs(words, term):
	conjs = []
	temp = term
	while "conj" in words[temp] and temp not in conjs:
		temp = words[temp]["conj"]
		conjs.append(temp)
	return conjs

def isNeg(words, term):
	if "neg" in words[term]:
		return True
	return False

def isDependency(key):
	if key not in wordattr:
		return True
	return False