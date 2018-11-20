import mmh3

def jaccard(sig1, sig2):
    S = set(sig1)
    T = set(sig2)
    return len(S & T) / len(S | T)


class Signatures:
    
    def __init__(self, filename):
        self.q = 3
        self.k = 1000
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
    
    def shingles (self):
        document = self.filetext
        document = document.replace('.','').replace(',','').replace('\n','').replace(':','').replace(';','').replace('_','').replace('-','')
        d = document.split(" ")
        shingles = [d[i:i+self.q] for i in range(len(d)-self.q)]
        
        return shingles
  
    def minHash (self):
        
        shingles = self.shingles()
        minValues = [min(self.listhash(shingle, seed) for shingle in shingles) for seed in range(self.k)]
        
        return minValues
        
    def getSignatures (self):
        return self.minHash()