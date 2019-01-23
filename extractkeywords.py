import chardet, string
import pandas as pd
import numpy as np

from modules.processtring import *

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
stop_words = set(stopwords.words('english'))
punctuation = set(string.punctuation)
nouns = ["NN", "NNS", "NNP", "NNPS"]
verbs = ["VBD", "VB", "VBG", "VBN","VBP", "VBZ"]

def extract():
    df = pd.read_csv('./modules/keywords/reviews.csv', encoding="utf8", sep='|', error_bad_lines=False)

    texts = []

    for text in  df.iloc[:,5]:
        texts.append(" ".join(getKeywords(text))) #+= " ".join(getKeywords(text)) + " "

    # wordlist = texts.split()

    # uniquewordlist = list(set(texts.split()))
    
    # wordfreq = []
    # for w in uniquewordlist:
    #     wordfreq.append(wordlist.count(w))

    # scores = zip(uniquewordlist, wordfreq)

    texts = texts

    for text in  df.iloc[:,5]:
        texts.append(" ".join(getKeywords(text)))

    vectorizer = TfidfVectorizer(encoding='utf-8', decode_error='ignore', lowercase=True, ngram_range=(1,1))
    freqs = vectorizer.fit_transform(texts)

    scores = zip(vectorizer.get_feature_names(),
                 np.asarray(freqs.sum(axis=0)).ravel())
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    words = [item[0] for item in sorted_scores[0:250]]
    scores = [item[1] for item in sorted_scores[0:250]]

    json = {'word': words, 'score': scores}
        
    outdf = pd.DataFrame(json)

    outdf.to_csv('./modules/keywords/keywords.csv')

extract()
