import sys
import os
import mmh3
import re
from timeit import default_timer as timer


#################### Utilities ######################
#hashes a list of strings
def listhash(l,seed):
	val = 0
	for e in l:
		val = val ^ mmh3.hash(e, seed)
	return val 



################### Similarity ######################
q = 3 # length of shingle
k = 100 # number of minhashes
docs = {} #dictionary mapping document id to document contents

# read data sets
srcfolder = os.path.dirname(os.path.abspath(__file__))
datafolder = os.path.join(srcfolder, "data")   # change to ats_corpus for large data set

for file in os.listdir(datafolder):
    filepath = os.path.join(datafolder, file)
    f = open(filepath, 'r')
    docs[file] = f.read()
    print("read document " + file)
    f.close()

# Create shingles
def shingles(q, s):
    words = re.findall(r'\w+[-\w]+[^\W_]+', s.replace('- \n', ''))
    return [[word for word in words[i:q+i]] for i in range( len(words)-q )]

def minhash(shingles, seed):
    return min(listhash(shingle, seed) for shingle in shingles)

def signature(shingles, k):
    return [minhash(shingles, seed) for seed in range(k)]

def signatures(docs):
    # sigsDict = {}
    # for docName, docContents in docs.items():
    #     shingle = shingles(q, docContents)
    #     sig = signature(shingle, k)
    #     sigsDict[docName] = sig
    return {docName: signature(shingles(q, docContents), k) for docName, docContents in docs.items()}

def jaccard(doc1, doc2):
    S = set(signature(shingles(q, docs[doc1]), k))
    T = set(signature(shingles(q, docs[doc2]), k))
    return len(S & T) / len(S | T)
# _shingles = shingles(q, docs['calltounconv00baxt.txt'])
# print(_shingles)
# _signature = signature(_shingles, k)
# print(_signature)
print(jaccard('remember00palm.txt', 'remembermeorholy00palm.txt'))