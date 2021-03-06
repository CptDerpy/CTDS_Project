from collections import Counter
from wordcloud import WordCloud as _WordCloud
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

class WordCloud:
    
    def __init__(self, filename, numOfWords = 10):
        self.filename = filename
        self.numOfWords = numOfWords
        self.filetext = self.loadFile(filename)
        self.cloud = self.makeCloud(self.filetext.lower())
    
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
        wordcloud = _WordCloud(background_color='white')
        countNumOfWords = dict(countTF.most_common(self.numOfWords))
        wordcloud.generate_from_frequencies(frequencies=countNumOfWords)
        return wordcloud

    def getCloud(self):
        return self.cloud
