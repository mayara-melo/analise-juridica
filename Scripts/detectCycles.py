#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
#from pymongo import pymongo.ASCENDING

client = MongoClient('localhost', 27017)
db = client.DJs
collection = db.all

n = 1000
#for acordao in collection.find():
#    print acordao.relator

path = [[float("inf") for x in range(n+1)] for x in range(n+1)] 

i = 1


def indexAcordaos():
    for acordao in collection.find():
        acordao['index'] = i
        collection.save( acordao)
        i += 1

for acordao in collection.find().limit(n):
    for quote in acordao["citacoes"]:
        i = acordao["index"]
        j = acordao["index"]
        path[i][j] = 1

def FloydWarshallWithPathReconstruction():
    for k in range(0,n):
        for docI in collection.find().sort("index").limit(n):
            for docJ in collection.find().sort("index").limit(n):
                i = docI["index"]
                j = docJ["index"]
                if path[i][k] + path[k][j] < path[i][j]:
                    path[i][j] = path[i][k] + path[k][j]
#                    path[i][j].clear()
 #                   next[i][j].push_back(k) // assuming its a c++ vector
                elif path[i][k] + path[k][j] == path[i][j] and k != j and k != i:
                    print k
  #                  next[i][j].push_back(k)

FloydWarshallWithPathReconstruction()
