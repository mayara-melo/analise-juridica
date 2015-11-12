#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from datetime import datetime
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

def FloydWarshallWithPathReconstruction( nTotal, links):
    nIsOdd = nTotal%2
    for k in range(1,K):
        for i in range( 1,nTotal+1):
            ik = pathLength( i,k, links)
            #for j in range( 1,nTotal+1):
            for j in range( 1,(nTotal/2)+1, 2):
                ij = pathLength( i,j, links) 
                kj = pathLength( k,j, links)
                ikj = ik + kj
                if ij > ikj:
                    setPathLength( i, j, ikj, links)
                ij = pathLength( i,j+1, links) 
                kj = pathLength( k,j+1, links)
                ikj = ik + kj
                if ij > ikj:
                    setPathLength( i, j+1, ikj, links)
	    if nIsOdd:
	    	ij = pathLength( i,nTotal, links) 
            	kj = pathLength( k,nTotal, links)
            	ikj = ik + kj
            	if ij > ikj:
                    setPathLength( i, nTotal, ikj, links)
        printProgress()

def findCycle(links, maxCiclo):
    count = 0
    for node, nodeLinks in links.items():
        if node in nodeLinks:
            tamCycle = nodeLinks[ node]
            if tamCycle > 1:
                count +=1
                with open('ciclosDetectados%s' %datetime.now(), 'a') as f:
                    f.write("max ciclo:%d:\nciclo tam %d\n" %(maxCiclo, tamCycle))
    with open('ciclosDetectados%s' %(datetime.now()), 'a') as f:
        f.write("%d ciclos encontrados\n\n" %count)

def printLinks(links):
    with open("printLinks%s" %(datetime.now()), "a") as f:
        for i, s in links.items():
            f.write( "%d: " %i)
            for q,l in s.items():
                f.write( "(%d: %d) " % (q, l))
            f.write( "\n")
            
def printProgress():
    global count
    global progress
    global onePercent
    count += 1
    if count >= onePercent:
        count = 0
        progress += 1
#            if not percentage % 10:
        with open("cicloDetect%s" %(datetime.now())) as f:
	     f.write("\r%d%%-%s\n" %(progress, datetime.now()))
	#sys.stdout.write("\r%d%%" % progress)
        #sys.stdout.flush()


def indexAcordaos( collection):
    i = 1
    acordaosIdIndexes = {}
    links = {}
    for acordao in collection.find():
        acordaoId = acordao['acordaoId']
        if acordaoId not in acordaosIdIndexes:
            acordaosIdIndexes[acordaoId] = i
            i+=1
        for quoteId in acordao['citacoes']:
            if quoteId not in acordaosIdIndexes:
                acordaosIdIndexes[ quoteId] = i
                i+=1
            addLink( i, acordaosIdIndexes[quoteId], 1, links)
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
collection = db['stf_pr1']
count = progress = 0
onePercent = collection.count()/100

print "indexing acordaos"
[acordaosIdIndexes, links] = indexAcordaos(collection)
#links = teste()
nTotal = len(acordaosIdIndexes)
#nTotal = 4
onePercent = nTotal/100

print "floyd warshall"
try:
    FloydWarshallWithPathReconstruction( nTotal, links)
except Exception as ex:
    with open('cicloReportSTFfaster', 'w') as f:
        f.write("erro floydWarshall as %s: %s" %(datetime.now(), ex))
    exit() 
print "findind cycle"
try:
    findCycle(links)
except Exception as ex:
    with open('cicloReportSTFfaster', 'a') as f:
        f.write("erro no findCycle %s: %s" %(datetime.now(), ex))
    exit()
try:
    printLinks(links)
except Exception as ex:
    with open('cicloReportSTFfaster', 'a') as f:
        f.write("erro em printLinks %s: %s" %(datetime.now(), ex))
    exit()
