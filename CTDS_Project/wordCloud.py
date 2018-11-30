# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 11:41:42 2018

@author: Andreas Hjort
"""

from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords 

class wordCloud:
    
    def __init__(self, filename, numOfWords = 10):
        self.filename = filename
        self.numOfWords = numOfWords
        self.filetext = self.loadFile(filename)
        self.makeCloud(self.filetext)
        
    
    def loadFile(self, filename):
        file = open(filename, encoding="utf8")
        return file.read()
    
    def makeCloud(self, fileText):
        
        stopwordslist = set(stopwords.words('english'))
        tokenizer = RegexpTokenizer(r'\w+')
        token = tokenizer.tokenize(fileText)
        tokens = [w for w in token if w not in stopwordslist]
        count = Counter(tokens)
        countTF =  Counter({k:float(v)/float(len(fileText)) for k,v in count.items()})
        wordcloud = WordCloud(background_color='white')
        countNumOfWords = dict(countTF.most_common(self.numOfWords))
        wordcloud.generate_from_frequencies(frequencies=countNumOfWords)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
