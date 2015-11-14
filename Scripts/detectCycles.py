#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from datetime import datetime
from datetime import date
import sys

def addLink( nodeFrom, nodeTo, pathLength, links):
    if nodeFrom not in links:
        links[ nodeFrom] = {}
    links[ nodeFrom][ nodeTo] = pathLength

def pathLength( nodeFrom, nodeTo, links):
    nodesTo = links.get( nodeFrom, {})
    return nodesTo.get( nodeTo, float('inf'))

def setPathLength( nodeFrom, nodeTo, length, links):
    links[ nodeFrom][ nodeTo] = length

def FloydWarshallWithPathReconstruction( nTotal, links, maxCycleLen):
    inf = float('inf')
    for k in range(1,nTotal+1):
#        print 'k--: %d' %k
        #for i in range( 1,nTotal+1):
        for i in range( 1,nTotal+1):
            ik = pathLength( i,k, links)
            if ik < maxCycleLen:
                nodesFromK = links.get( k, {})
                for j in nodesFromK:
                    ij = pathLength( i,j, links) 
                    kj = nodesFromK.get(j)
                    ikj = ik + kj
                    if ij > ikj and ikj <= maxCycleLen:
                        setPathLength( i, j, ikj, links)
#        for i in range( 1,nTotal+1):
 #           ik = pathLength( i,k+1, links)
  #          if ik < maxCycleLen:
   #             nodesFromK = links.get( k+1, {})
    #            for j in nodesFromK:
     #               ij = pathLength( i,j, links) 
      #              kj = nodesFromK.get(j)
       #             ikj = ik + kj
        #            if ij > ikj and ikj <= maxCycleLen:
         #               setPathLength( i, j, ikj, links)
          #              ik = pathLength( i,k+1, links)
#           ik = pathLength( i+1,k+1, links)
 #           if ik < maxCycleLen:
  #              nodesFromK = links.get( k+1, {})
   #             for j in nodesFromK:
    #                ij = pathLength( i+1,j, links) 
     #               kj = nodesFromK.get(j)
      #              ikj = ik + kj
       #             if ij > ikj and ikj <= maxCycleLen:
        #                setPathLength( i+1, j, ikj, links)
         #               ik = pathLength( i+1, k+1, links)

        printProgress()

def findCycle(links, maxCiclo, indexesByAcordaosIds):
    count = 0
    acordaosIdsByIndexes = dict((v, k) for k, v in indexesByAcordaosIds.items())
    for node, nodeLinks in links.items():
        if node in nodeLinks:
            tamCycle = nodeLinks[ node]
            if tamCycle > 1:
                count +=1
                with open('ciclosDetectados', 'a') as f:
                    f.write("ciclo acordao %d-%s tam %d\n" %( node, acordaosIdsByIndexes[node], tamCycle))
    with open('ciclosDetectados', 'a') as f:
        f.write("%d ciclos encontrados\n\n" %count)

def printLinks(links):
    with open("cicloLinks%s" %(datetime.now()), "a") as f:
        for i, s in links.items():
            f.write( "%d: " %i)
            for q,l in s.items():
                f.write( "(%d: %d) " % (q, l))
            f.write( "\n")
            
def printProgress():
    global count
    global progress
    global onePercent
    count += 3
    if count >= onePercent:
        count = 0
        progress += 1
#            if not percentage % 10:
        with open("cicloDetectProgress", 'a') as f:
	     f.write("\r%d%%-%s\n" %(progress, datetime.now()))
	#sys.stdout.write("\r%d%%" % progress)
        #sys.stdout.flush()


def indexAcordaos( collection):
    i = 1
    acordaosIdIndexes = {}
    links = {}
    for acordao in collection.find({}, {'acordaoId':1}):
        acordaosIdIndexes[acordao['acordaoId']] = i
        i+=1 
    for acordao in collection.find({}, {'acordaoId':1, 'citacoes':1}):
        acordaoId = acordao['acordaoId']
        for quoteId in acordao['citacoes']:
            if quoteId in acordaosIdIndexes:
                addLink( acordaosIdIndexes[acordaoId], acordaosIdIndexes[quoteId], 1, links)
    return [acordaosIdIndexes,links]

def teste():
    links = {}
    links[1] = {3:-2}
    links[2] = {1:4, 3:3}
    links[3] = {4:2}
    links[4] = {2:-1}
    return links

i = 1
K = int(sys.argv[1])
client = MongoClient('localhost', 27017)
db = client.DJs
collection = db['all_pr1']
count = progress = 0
onePercent = collection.count()/100

print "indexing acordaos"
[acordaosIdIndexes, links] = indexAcordaos(collection)
nTotal = len(acordaosIdIndexes)
#links = teste()
#nTotal = 4
onePercent = nTotal/100

print "floyd warshall"
try:
    FloydWarshallWithPathReconstruction( nTotal, links, K)
except Exception as ex:
    print "exception"
    with open('cicloReport', 'w') as f:
        f.write("erro floydWarshall as %s: %s" %(datetime.now(), ex))
    exit() 
print "findind cycle"
try:
    findCycle(links, K, acordaosIdIndexes)
except Exception as ex:
    timeNow = datetime.now()
    print "exception"
    with open('cicloReport', 'a') as f:
        f.write("erro no findCycle %s: %s" %(timeNow, ex))
    exit()
try:
    printLinks(links)
except Exception as ex:
    timeNow = datetime.now()
    print "exception"
    with open('cicloReport', 'a') as f:
        f.write("erro em printLinks %s: %s" %(timeNow, ex))
    exit()
