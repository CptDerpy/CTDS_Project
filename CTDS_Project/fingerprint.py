import mmh3
import re
from nltk.corpus import stopwords

def jaccard(sig1, sig2):
    S = set(sig1)
    T = set(sig2)
    return len(S & T) / len(S | T)

def new_jaccard(sig1, sig2):
    S = set(sig1)
    T = set(sig2)
    # print(S & T)
    return len(S & T) / len(S)


class Fingerprint:
    
    def __init__(self, filename):
        self.q = 5
        self.k = 100
        self.filename = filename
        self.filetext = self.loadFile(filename)

    def loadFile(self, filename):
        file = open(filename, encoding="utf8")
        return file.read()
  
    def listhash(self, shingle, seed):
        val = 0
        for e in shingle:
            val = val ^ mmh3.hash(e, seed)
        return val
    
    def shingles(self, q):
        sw = set(stopwords.words('english'))
        document = self.filetext
        document = re.findall(r'\w+[-\w]+[^\W_]+', document)
        document = [w for w in document if w not in sw]
        shingles = [document[i:i+q] for i in range(len(document)-q)]
        return shingles

    def shingles2(self, q):
        sw = set(stopwords.words('english'))
        document = self.filetext
        document = re.findall(r'\w+[-\w]+[^\W_]+', document)
        shingles = [document[i:i+q] for i in range(len(document)-q)]
        return shingles
  
    def minHash(self):
        shingles = self.shingles(self.q)
        minValues = [min(self.listhash(shingle, seed) for shingle in shingles) for seed in range(self.k)]
        return minValues
        
    def getSignatures(self):
        return self.minHash()

    def getSubstring(self):
        shingles = self.shingles2(5)
        return [(s1,s2,s3,s4,s5) for s1,s2,s3,s4,s5 in shingles]
