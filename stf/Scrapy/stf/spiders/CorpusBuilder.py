#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


class CorpusBuilder:

    def __init__( self):
        self.corpusDict = {}
        self.text = ""
        self.stopListWords = [

        ]

    def addWords( self, text):
        keys = self.corpusDict.keys()
        for w in re.split(r"[\s\(\),.?;:\"\']+", text):
#            w = w.decode("utf-8").encode("iso-8859-1")
            w = w.decode("utf-8")
            w = w.lower()
            w = w.encode("utf-8")
            if w in keys:
                self.corpusDict[ w] += 1
            else:
                if self.validWord( w):
                    self.corpusDict[ w] = 1
    
    def validWord( self, word):
        if len( word) < 3: return 0
        if re.match( r"[\d]+", word): return 0 
        if re.match( r"qu[e(?:ai)(?:al)]", word): return 0 
        if re.match( r"d[aeio][s]?", word): return 0 
        if word == "não": return 0 
        if re.match( r"p[(?:ara)(?:elo)(?:or)][s]?", word): return 0 
        return 1

    def print2File( self, filename):
        file = open( filename, 'a')
        file.seek(0)
        file.truncate()
        for w in sorted(self.corpusDict, key=self.corpusDict.get, reverse=True):
#            w = k.decode("utf-8").encode("iso-8859-1")
#            file.write( '{0:20} ==> {1:10d}'.format( k.encode('utf8'), dic[k]) )
            file.write( '%20s ==> %10d\n' % (w, self.corpusDict[w]))
   #         print k
  #          file.write( w)
   #         file.write( str(dic[k]))
    #        file.write( "\n\n")
        file.close() 

