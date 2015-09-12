#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from Acordao import Acordao
import sys
from datetime import datetime

def buildMap( collection, query):
    acordaos = []
    quotes = {}
    quotedBy = {}
    similars = {}
    docsFound = collection.find( query, no_cursor_timeout=False)
    print docsFound.count()
    for acordao in docsFound:
        acordaoId = acordao['acordaoId']
        quotes[ acordaoId] = set()
        quotedBy[ acordaoId] = set()
        similars[ acordaoId] = set()
        for quotedId in acordao['citacoes']:
            queryWithId = query.copy()
            queryWithId['acordaoId'] = quotedId
            if collection.find_one( queryWithId):
                quotes[ acordaoId].add( quotedId)
                if quotedId not in quotedBy:
                    quotedBy[ quotedId] = set()
                quotedBy[ quotedId].add( acordaoId)
        for similar in acordao['similares']:
            similarId = similar['acordaoId']
            if similarId not in similars:
                similars[ similarId] = set()
                similarAcordaoObj = Acordao( similarId, acordao['tribunal'], similar['relator'], True)
                acordaos.append( similarAcordaoObj)
            if acordaoId not in similars:
                similars[ similarId] = set()
            similars[ similarId].add( acordaoId)
            similars[ acordaoId].add( similarId)
        acordaoObj = Acordao( acordaoId, acordao['tribunal'], acordao['relator'], False)
        acordaos.append( acordaoObj)
        printProgress()
    return [quotes, quotedBy, similars, acordaos]

def insertNodes( collectionOut, acordaos, quotes, quotedBy, similars):
    for doc in acordaos:       
#    for doc, docQuotes in quotes.items():
        docId = doc.getId()
        docQuotedBy = quotedBy.pop( docId, set())
        docQuotes = quotes.pop( docId, set())
        docSimilars = similars.pop( docId, set())
        collectionOut.insert(
                                {'acordaoId': docId
                                ,'citacoes' : list(docQuotes)
                                ,'citadoPor': list(docQuotedBy)
                                ,'similares': list(docSimilars)
                                ,'relator':  doc.getRelator()
                                ,'tribunal': doc.getTribunal()
                                ,'virtual': doc.getVirtual()
                                })

def addVirtualNodes( collectionIn, collectionOut):
    for acordao in collectionIn.find( no_cursor_timeout=False):
        mainAcordaoId = acordao['acordaoId']
    #add similar acordaos as virtual nodes (new documents)
        for similar in acordao["similares"]:
            similarId = similar['acordaoId']
        #se o acordao similar estiver na colecao principal atualiza os dados com os dados desse documento
            result = collectionOut.update_one(
                                            {'acordaoId': similarId}
                                            ,{  '$set': {'relator': similar['relator']
                                                        ,'dataJulg': similar['dataJulg']
                                                        ,'orgaoJulg': similar['orgaoJulg']
                                                        ,'localSigla': similar['localSigla']
                                                        ,'virtual': True },
                                                '$addToSet': {'similares':mainAcordaoId}
                                             }
                                            ,upsert=True )
        printProgress()



def addAcordaosSimilaresNormalizados( collection, collectionOut):
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
        printProgress()


def printProgress():
    global count
    global percentage
    global onePercent
    count+=1
    if count >= onePercent:
        count = 0
        percentage+=1
#        if not percentage % 10:
        sys.stdout.write("\r%d%%" % percentage)
        sys.stdout.flush()

#collectionNormalized.drop()
#collectionGraph.drop()
#addVirtualNodes( collectionAcordaos, collectionNormalized)
#addAcordaosSimilaresNormalizados( collectionAcordaos, collectionNormalized)
client = MongoClient('localhost', 27017)
db = client.DJs
collectionAcordaos = db['acordaos']
collectionGraph = db['graphSTF']
#collectionNormalized = db['comNosVirtuais']
totalAcordaos = collectionAcordaos.count()
onePercent = totalAcordaos/100
count = 0
percentage = 0
quotes = {}
quotedBy = {}
similars = {}
acordaos = []
t1 = datetime.now()
[quotes, quotedBy, similars, acordaos] = buildMap( collectionAcordaos, {"tribunal": "STF", "localSigla": "PA"})
t2 = datetime.now()
print "buildMap took %d" % ((t2-t1).seconds)
t1 = datetime.now()
insertNodes( collectionGraph, acordaos, quotes, quotedBy, similars)
t2 = datetime.now()
print "insertNodes took %d" % ((t2-t1).seconds)
