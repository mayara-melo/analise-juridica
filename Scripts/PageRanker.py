#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from Acordao import Acordao
import sys
import math
from decimal import Decimal
from datetime import datetime

class PageRanker:
    
    epsilon = Decimal(1.0E-18)
    d = Decimal(0.85)

    def __euclidianDistance( self, pMap, qMap):
        totalSum = 0.0
        for docId, p in pMap.items():
            q = qMap[ docId]
            term = math.pow( (p-q) , 2)
            totalSum += term
        dist = math.sqrt( totalSum)
        print dist
        return dist

    def __pageRank1sum( self, quotingAcordaos, pageRanks, quotesLen):
        totalSum = Decimal(0)
        for docId in quotingAcordaos:
            pr = pageRanks.get( docId, 0.0 )
            l = quotesLen.get(docId, 1)
            term = pr/l
#            terms.append( pr/l)
            totalSum += term
        return totalSum

    def __lengthArray( self, array):
        lengthArray = {}
        for x, s in array.items():
            lengthArray[x] = len(s)
        return lengthArray

    def __pageRank2sum( self, quotingAcordaos, pageRanks, quotesLen):
        totalSum = Decimal(0.0)
        for docId in quotingAcordaos:
            totalSum += pageRanks.get( docId, 0.0)
        return totalSum

    def calculatePageRanks( self, acordaos, quotes, quotedBy, mode):
        epsilon = PageRanker.epsilon
        d = PageRanker.d
        pageRanks = {}
        nDocs = len( acordaos)
        for docId in acordaos:
            pageRanks[ docId] = Decimal(1.0)/Decimal(nDocs)
        newPageRanks = {}
        rounds = 0
        prSumFunc = self.__pageRank1sum
        if mode == 2:
            prSumFunc = self.__pageRank2sum
        quotesLen = self.__lengthArray( quotes)
        while( True):
            t1 = datetime.now()
            for docId in acordaos:
                quotingAcordaos = quotedBy.get( docId, [])
                totalSum = prSumFunc( quotingAcordaos, pageRanks, quotesLen)
                newPageRanks[docId] = ((Decimal(1.0) - d) / Decimal(nDocs)) + (d * totalSum)
  #          print "calculando pr %d" % ((datetime.now()-t1).microseconds)
            rounds += 1
            t1 = datetime.now()
            if( self.__euclidianDistance( pageRanks, newPageRanks) < epsilon):
                break
 #           print "euclidian distande %d" % ((datetime.now()-t1).seconds)
            pageRanks.clear()
            t1 = datetime.now()
            pageRanks = newPageRanks.copy()
#            print "copying newpr %d" % ( (datetime.now()-t1).seconds)
     	print("rounds: %d" % rounds)
        return pageRanks
