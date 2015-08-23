#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import sys

dbName = sys.argv[1]
collectionName = sys.argv[2]
client = MongoClient('localhost', 27017)
db = client[dbName]
collectionAcordaos = db[collectionName]
totalAcordaos = collectionAcordaos.count()
acordaosIds = {}

nTotalDuplicates = 0
nDuplicates = 0


for acordao in collectionAcordaos.find():
    acordaoId = acordao['acordaoId']
    if acordaoId in acordaosIds:
        acordaosIds[ acordaoId] += 1
    else:
        acordaosIds[ acordaoId] = 1
for ID in acordaosIds:
    if acordaosIds[ID] > 1:
        print( ID)
        nTotalDuplicates += acordaosIds[ID]
        nDuplicates += 1


print( nTotalDuplicates)
print( nDuplicates)
        
