#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from datetime import datetime
from datetime import date
from threading import Thread
import sys
import traceback

def addLink( nodeFrom, nodeTo, value, links):
    if nodeFrom not in links:
        links[ nodeFrom] = {}
    links[ nodeFrom][ nodeTo] = value

def pathLength( nodeFrom, nodeTo, links):
    nodesTo = links.get( nodeFrom, {})
    return nodesTo.get( nodeTo, float('inf'))

def setPathLength( nodeFrom, nodeTo, length, links):
    links[ nodeFrom][ nodeTo] = length

def pathNext( nodeFrom, nodeTo, next):
    nodesTo = next.get( nodeFrom, {})
    return nodesTo.get( nodeTo, False)

def findPathI2JThoughK( iMin, iMax, nodesFromK, k, links, maxCycleLen, next):
#    print "i: %d-%d" %(iMin, iMax)
    for i in xrange( iMin, iMax):
        ik = pathLength( i,k, links)
        if ik < maxCycleLen:
            for j, kj in nodesFromK.iteritems():
                ij = pathLength( i,j, links) 
                ikj = ik + kj
                if ij > ikj and ikj <= maxCycleLen:
                    setPathLength( i, j, ikj, links)
                    setPathLength( i, j, pathNext(i,k,next), next)

def FloydWarshallWithPathReconstruction( nTotal, links, maxCycleLen, next):
    nThreads = 2 
    nSteps = nTotal/nThreads
    threads = []
    for k in xrange(1,nTotal+1):
#        print 'k--: %d' %k
        nodesFromK = links.get( k, {})
        s = 1
        for n in xrange(nThreads):
            t = Thread(target=findPathI2JThoughK, args=(s, s+nSteps, nodesFromK, k, links, maxCycleLen, next))
            threads.append(t)
            s += nSteps
            t.start()
        for t in threads:
            t.join()
            
#        for i in xrange( 1,nTotal+1):
 #           ik = pathLength( i,k, links)
  #          if ik < maxCycleLen:
   #             for j, kj in nodesFromK.iteritems():
    #                ij = pathLength( i,j, links) 
     #               ikj = ik + kj
      #              if ij > ikj and ikj <= maxCycleLen:
       #                 setPathLength( i, j, ikj, links)
        #                setPathLength( i, j, pathNext(i,k,next), next)

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

def findCycle( indexesByAcordaosIds, links, next, maxCycleLen):
    count = 0
    cycles = {}
    cyclesCount = 0
    acordaosIdsByIndexes = dict((v, k) for k, v in indexesByAcordaosIds.items())
    for i in acordaosIdsByIndexes:
        nodesFromI = links.get(i, {})
        for j in nodesFromI:
            if pathLength(j,i, links) == 1:
                cycle = path( i, j, next)
                if not cycle:
                    print cycle
                    print '%d-%d len:%d'%(i,j,pathLength(i,j,links))
                cyclesCount += 1
                cycleLength = len(cycle)
                with open('ciclosDetectados', 'a') as f:
                    for n in cycle:
                        f.write("-> %s" %( acordaosIdsByIndexes[n]))
                    f.write('\n---tam %d---------\n\n' %cycleLength)
    with open('ciclosDetectados', 'a') as f:
        f.write("\n\n\n%d ciclos virtuais encontrados\n\n" %cyclesCount)

def path( i, j, next):
    nextNode = pathNext(i,j, next)
    if not nextNode:
        return False
    path = [i]
    while i != j:
        i = next[i][j]
        path.append(i)
    return path

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
    count += 1 
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
    next = {}
    for acordao in collection.find({}, {'acordaoId':1}):
        acordaosIdIndexes[acordao['acordaoId']] = i
        i+=1 
    for acordao in collection.find({}, {'acordaoId':1, 'citacoes':1}):
        acordaoId = acordao['acordaoId']
        for quoteId in acordao['citacoes']:
            if quoteId in acordaosIdIndexes:
                index = acordaosIdIndexes[acordaoId]
                quotedIndex = acordaosIdIndexes[quoteId]
                addLink( index, quotedIndex, 1, links)
                addLink( index, quotedIndex, quotedIndex, next)
    return [acordaosIdIndexes,links, next]

def teste():
    links = {}
    next = {}
    index = {}
    links[1] = {3:1}
    links[2] = {1:1, 3:1}
    links[3] = {4:1}
    links[4] = {2:1}
    next[1] = {3:3}
    next[2] = {1:1, 3:3}
    next[3] = {4:4}
    next[4] = {2:2}
    index['A'] = 1
    index['B'] = 2
    index['C'] = 3
    index['D'] = 4
    return [index, links, next]

i = 1
K = int(sys.argv[1])
client = MongoClient('localhost', 27017)
#db = client.DJs
#collection = db['all_pr1']
db = client.acordaos
collection = db['stf']
count = progress = 0
onePercent = collection.count()/100

print "indexing acordaos"
[acordaosIdIndexes, links, next] = indexAcordaos(collection)
nTotal = len(acordaosIdIndexes)
#[acordaosIdIndexes, links, next] = teste()
#nTotal = 4
onePercent = nTotal/100

print "floyd warshall"
try:
    FloydWarshallWithPathReconstruction( nTotal, links, K, next)
except Exception as ex:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback))
    print repr(traceback.extract_tb(exc_traceback))
    print repr(traceback.format_tb(exc_traceback))
    print exc_traceback.tb_lineno
    with open('cicloReport', 'w') as f:
        f.write("erro floydWarshall as %s: %s\n" %(datetime.now(), ex))
    exit() 
print "findind cycle"
try:
    findCycle( acordaosIdIndexes, links, next, K)
except Exception as ex:
    timeNow = datetime.now()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback))
    print repr(traceback.extract_tb(exc_traceback))
    print repr(traceback.format_tb(exc_traceback))
    print exc_traceback.tb_lineno

    with open('cicloReport', 'a') as f:
        f.write("erro no findCycle %s: %s\n" %(timeNow, ex))
    exit()
try:
    printLinks(links)
except Exception as ex:
    timeNow = datetime.now()
    print ex 
    with open('cicloReport', 'a') as f:
        f.write("erro em printLinks %s: %s\n" %(timeNow, ex))
    exit()
