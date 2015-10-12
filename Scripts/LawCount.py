import sys
from pymongo import MongoClient
from Acordao import Acordao
from bson.code import Code
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl

#dbName = sys.argv[1]
#collectionInName = sys.argv[2]
#outFilename = sys.argv[3]
dbName = sys.argv[1]
collectionInName = sys.argv[2]
outFilename = "plot"
client = MongoClient('localhost', 27017)
db = client[ dbName]
collectionIn = db[ collectionInName]
query = {}

lawsCount = {}
d = {}
maxCount = 0
nLaws = 0
totalRefs = 0
lawsInfo = {}
for doc in collectionIn.find():
    legislacao = doc['legislacao']
    for lei in legislacao:
        if not lei:
            continue
        refs = lei.get('refs', '')
        ano  = lei.get('ano','')
        desc = lei.get('descricao', '')
        tipo = lei.get('tipo', '')
        sigla = lei.get('sigla','')
        if sigla not in d:
            d[sigla] = 0
            lawsInfo[sigla] = {}
            nLaws += 1
        lawsInfo[sigla]['refs'] = refs
        lawsInfo[sigla]['desc'] = desc
        lawsInfo[sigla]['ano'] = ano
        lawsInfo[sigla]['tipo'] = tipo
        d[sigla] += 1
        totalRefs += 1
        if d[sigla] > maxCount:
            maxCount = d[sigla]

avg = float(totalRefs)/float(maxCount)
print 'totalRefs %d' %totalRefs
print 'avg %f' %avg
print 'max count %d' %maxCount

i=0
for w in sorted(d, key=d.get, reverse=True):
    i +=1
    sigla = w
    leg = '%s %s' %(lawsInfo[sigla]['desc'],lawsInfo[sigla]['ano'])
    lawsCount[leg] = d[w]
    if i == 10:
        break
#print w, d[w]

X = np.arange(len(lawsCount))
pl.barh(X, lawsCount.values(), height=0.6, align='center', color='purple', left=0.25)
pl.yticks(X, lawsCount.keys())
#ymax = max(lawsCount.values()) + 1
#pl.ylim(0, ymax)
pl.show()
