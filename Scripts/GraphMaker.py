#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from Acordao import Acordao
import sys

class GraphMaker():

    def __init__( self, dbName, collectionInName, collectionOutName):
        client = MongoClient('localhost', 27017)
        db = client[ dbName]
        self.collectionIn = db[ collectionInName]
        self.collectionOut = db[ collectionOutName]
        self.collectionOut.drop()
        self.onePercent = self.collectionIn.count()/100
        self.count = 0
        self.progress = 0
#
    def __addElemSetToDict( self, aDict, elemKey, elemValue):
        if elemKey not in aDict:
            aDict[ elemKey] = set()
        aDict[ elemKey].add( elemValue)
        return aDict

    def removeInvalidAcordaosFromDicts( self, validAcordaos, quotes, quotedBy):
        for docId, quotesId in quotes.items():
            newQuotesId = set()
            for q in quotesId:
                if q in validAcordaos:
                    newQuotesId.add( q)
                else:
                    quotedBy.pop(q,0)
            quotes[ docId] = newQuotesId
        return [quotes, quotedBy]
        
    def buildDicts( self, query):
        acordaos = {}
        quotes = {}
        quotedBy = {}
        similars = {}
        print "building map"
        docsFound = self.collectionIn.find( query, no_cursor_timeout=True)
        nDocs = docsFound.count()
        self.onePercent = nDocs/100 
        self.count = self.progress = 0
        for doc in docsFound:
            docId = doc['acordaoId']
            for quotedId in doc['citacoes']:
                queryWithId = query.copy()
                queryWithId['acordaoId'] = quotedId
       #         if self.collectionIn.find_one( queryWithId):
                quotes = self.__addElemSetToDict( quotes, docId, quotedId)
                quotedBy = self.__addElemSetToDict( quotedBy, quotedId, docId)
            for similar in doc['similares']:
                similarId = similar['acordaoId']
                similars = self.__addElemSetToDict( similars, similarId, docId)
                similars = self.__addElemSetToDict( similars, docId, similarId)
                acordaos[ similarId] = Acordao( similarId, doc['tribunal'], similar['relator'], True)
            acordaos[ docId] = Acordao( docId, doc['tribunal'], doc['relator'], False)
            self.__printProgress()
        return [acordaos, quotes, quotedBy, similars]

    def insertNodes( self, acordaos, quotes, quotedBy, similars, pageRanks):
        nDocs = len(acordaos)
        self.onePercent = nDocs/100 
        self.count = self.progress = 0
        insertStep = nDocs
        if nDocs > 10000:
            insertStep = 10000
        print "n acordaos %s to be inserted" % nDocs
        i = 0 
        docs2Insert = []
        for docId, doc in acordaos.items():
            docQuotedBy = list( quotedBy.get( docId, set()))
            docQuotes = list( quotes.get( docId, set()))
            docSimilars = list( similars.get( docId, set()))
            docPageRank = float( pageRanks.get( docId, 0.0))
            docs2Insert.append (
                      { 'acordaoId': docId
                        ,'citacoes' : docQuotes
                        ,'citadoPor': docQuotedBy
                        ,'similares': docSimilars
                        ,'relator':  doc.getRelator()
                        ,'tribunal': doc.getTribunal()
                        ,'pageRank': docPageRank
                        ,'virtual': doc.getVirtual()
                        })
            i += 1
            self.__printProgress()
            if i >= insertStep:
                self.collectionOut.insert( docs2Insert)
                docs2Insert = []
                i = 0
        if i > 0:
            self.collectionOut.insert( docs2Insert)
        

    def addAcordaosSimilaresNormalizados( self, collection, collectionOut):
        for acordao in collection.find( no_cursor_timeout=False):
            similarsIds = set()
            for similar in acordao['similares']:
                similarsIds.add( similar['acordaoId'])
            collectionOut.update_one( 
                                {'acordaoId': acordao['acordaoId']}
                                ,{  '$set': {'relator': acordao['relator']
                                ,'acordaoType': acordao['dataJulg']
                                ,'ementa'  : acordao['ementa']
                                ,'decisao' : acordao['decisao']
                                ,'citacoes': acordao['citacoes']
                                ,'legislacao': acordao['legislacao']
                                ,'tags'    : acordao['tags']
                                ,'partes'  : acordao['partes']
                                ,'tribunal': acordao['tribunal']
                                ,'dataJulg': acordao['dataJulg']
                                ,'orgaoJulg': acordao['orgaoJulg']
                                ,'localSigla': acordao['localSigla']
                                ,'local'   : acordao['local']
                                ,'virtual' : False },
                                '$addToSet': {'similares':{'$each':list( similarsIds)}}
                                }
                                ,upsert=True )
            self.printProgress()


    def __printProgress( self):
        self.count += 1
        if self.count >= self.onePercent:
            self.count = 0
            self.progress += 1
#            if not percentage % 10:
            sys.stdout.write("\r%d%%" % self.progress)
            sys.stdout.flush()

#collectionNormalized.drop()
#addVirtualNodes( collectionAcordaos, collectionNormalized)
#addAcordaosSimilaresNormalizados( collectionAcordaos, collectionNormalized)
