#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
#from pymongo import pymongo.ASCENDING
import sys
client = MongoClient('localhost', 27017)
db = client.DJs
collection = db['stfPR1']
count = progress = 0
onePercent = collection.count()/100
#for acordao in collection.find():
#    print acordao.relator

#path = [[float("inf") for x in range(n+1)] for x in range(n+1)] 

i = 1
links = {}
K = int(sys.argv[1])


def addLink( nodeFrom, nodeTo, pathLength):
    global links
    if nodeFrom not in links:
        links[ nodeFrom] = {}
    links[ nodeFrom][ nodeTo] = pathLength

def pathLength( nodeFrom, nodeTo):
    global links
    nodesTo = links.pop( nodeFrom, {})
    return nodesTo.pop( nodeTo, float('inf'))

def setPathLength( nodeFrom, nodeTo, length):
    links[ nodeFrom][ nodeTo] = length

def FloydWarshallWithPathReconstruction( nTotal):
    for k in range(1,K):
        print "k: %d" %k
        for i in range( nTotal):
            for j in range( nTotal):
#                pathI2J = [i]
#                i = docI["index"]
 #               j = docJ["index"]
#                if pathLength( i,k) > 0 and pathLength(k,j) > 0:
 #                   pathI2J.append( path( i,k).extend)
                if pathLength( i,j) > pathLength( i, k) + pathLength(k,j):
                    setPathLength( i, j, pathLength( i, k) + pathLength( k, j))
            printProgress()
        printLinks()
#                    path[i][j].clear()
 #                   next[i][j].push_back(k) // assuming its a c++ vector
#                elif pathLength( i,k) + pathLength( k,j) == pathLength(i,j) and k != j and k != i:
 #                   print k
  #                  next[i][j].push_back(k)

#links = {nodeFrom: {nodeTo: [path1, path2, ...]}  }

def findCycle():
    global links
    for node, nodeLinks in links:
        if node in nodeLinks:
            tamCycle = nodeLinks[ node]
            if tamCycle > 1:
                with open('ciclos detectados', 'a') as f:
                    f.write("ciclo tam %d\n" % tamCycle)

def printLinks():
    global links
    with open("cicloprint", "a") as f:
        for i, s in links.items():
            f.write( "%d: " %i)
            for q,l in s.item():
                f.write( "(%d: %d) " % (q, l))
            
#def indexAcordaos():
#    i = 1
#    for acordao in collection.find():
#        acordao['index'] = i
 #       collection.save( acordao)
  #      i += 1
   # return i
def printProgress():
    global count
    global progress
    global onePercent
    count += 1
    if count >= onePercent:
        count = 0
        progress += 1
#            if not percentage % 10:
        sys.stdout.write("\r%d%%" % progress)
        sys.stdout.flush()


def indexAcordaos():
    global acordaosIdIndexes
    i = 1
    for acordao in collection.find():
        acordaoId = acordao['acordaoId']
        if acordaoId not in acordaosIdIndexes:
            acordaosIdIndexes[acordaoId] = i
            i+=1
        for quoteId in acordao['citacoes']:
            if quoteId not in acordaosIdIndexes:
                acordaosIdIndexes[ quoteId] = i
                i+=1
            addLink( i, acordaosIdIndexes[quoteId], 1)
    return i

#def initialLinks():
 #   for Id, i in acordaosIdIndexes:
  #      acordao = collection.find({'acordaoId': Id}):
   #     for quotes in acordao['quotes']:
#            addLink( i, acordaosIdIndexes[],1)

acordaosIdIndexes = {}
#for acordao in collection.find():
 #   for quote in acordao["citacoes"]:
#        i = acordao["index"]
 #       j = quote["index"]
  #      addLink( i, j, 1)

print "indexing acordaos"
nTotal = indexAcordaos()
onePercent = nTotal/100
print "floyd warshall"
FloydWarshallWithPathReconstruction( nTotal)
print "findind cycle"
findCycle()
