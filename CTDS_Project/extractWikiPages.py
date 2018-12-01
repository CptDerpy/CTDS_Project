from urllib.request import urlopen
import json
import pandas as pd
import io

class extractWikiPages:
    
    def __init__(self,filename):
        self.extract(filename)
    
    def extract(self, filename):
        baseurl = "https://en.wikipedia.org/w/api.php?"
        action = "action=query"
        content = "prop=extracts&exlimit=max&explaintext"
        rvprop ="rvprop=timestamp|content"
        dataformat = "format=json"
        rvdir = "rvdir=older" #sort revisions from newest to oldest
        start = "rvend=2016-01-03T00:00:00Z" #start of my time period
        end = "rvstart=2020-01-03T00:00:00Z" #end of my time period
        limit = "rvlimit=1" #consider only the first revisionz
        
        
        database = pd.read_csv(filename,encoding="utf-8")
        
        members = database['WikiPageName'].unique()
        counter = 1
        for member in members:
            title = "titles=" + member
            print(str(counter) + "/100 files downloaded")
            query = "%s%s&%s&%s&%s&%s&%s&%s&%s&%s" % (baseurl, action, title, content, rvprop, dataformat, rvdir, end, start, limit)
            wikisource = urlopen(query)
            w = wikisource.read()
            wikiJSON = json.loads(w)
            d = wikiJSON['query']['pages']
            text = d[str(list(d.keys())[0])]['extract']
            toWrite = text.encode('utf-8').decode('unicode_escape')
            
            #file = open('Democratic.txt', 'a+')
            file = io.open("Wikipages/" + member + ".txt", mode="w", encoding="utf-8")
            file.write(toWrite)
            file.close()
            counter +=1
