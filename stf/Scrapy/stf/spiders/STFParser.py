# -*- coding: utf-8 -*-

from AcordaoParser import AcordaoParser

#from stf.items import StfLawItem
import re
#import time
from datetime import datetime, timedelta

class STFParser( AcordaoParser):

    def parseDataJulgamento( self, text):
        text = text.replace('&nbsp', '').strip()
        date = re.search('Julgamento:\s*(\d{2})\/(\d{2})\/(\d{4}).*', text)
        if date:
            return datetime( int(date.group(3)), int(date.group(2)), int(date.group(1)))
        return ''

    def parseOrgaoJulgador( self, text):
        text = text.replace('&nbsp', '').strip()
        match = re.search('Julgador:\s*(.*)\s*', text)
        if match:
            return match.group(1).strip()
        return ''

    def parseAcordaosQuotes( self, txt):
        quotes = []
        data = re.search(("Acórdão(?:\s*\(?s\)?)? citado(?:\s*\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])").decode("utf-8"), txt)
        if data:
            data = (data.group(1))
            data = re.split('[;,.()]', data)
            for q in data:
                q = q.strip()
                q = re.match("([a-zA-Z]{2,}[ -]\d+.*)", q)
                if q:
                    q = q.group(1)
                    q = q.replace('-', ' ')
                    q = q.strip().upper()
                    quotes.append( q) 
        return quotes
 
    def parseLaws( self, text):    
        laws = []
        law = {} 
        references ="" 
        lines = text.split("\n")
        for l in lines:
            l = l.encode("utf-8").upper()
            if l.startswith("LEG-"):
                if references:
                    refs = re.split("\s*(ART-[\w\d]+(?:\s+(?:INC|PAR|LET)-[\w\d]+)*)\s*", references.strip())
                    temp = refs
                    refs = []
                    for i,r in enumerate(temp):
                        r = r.strip()
                        if r.startswith("ART") or i == len(temp)-1:
                            refs.append( r)
                    if len( refs) > 1:
                        law["descricao"] = refs.pop()
                        law["artigos"] = refs
                    else:
                        law["descricao"] = references.strip()
                        law["artigos"] =[] 
                    laws.append( dict(law))
                    law ={} 
                    references ="" 
                law["sigla"] = self.getMatchText( l, r"\s*LEG-\w+\s+([^\s]+).*")
                law["tipo"] = self.getMatchText( l, r"\s*LEG-(\w+).*")
                law["ano"] = self.getMatchText( l, r".*ANO[-:](\d+).*")
            else:
                references = references.strip() + " "+l.strip()+""
        return laws
 
    def parseSimilarAcordaos( self, raw):
        similar = []
        lines = raw.split("\n")
        if len(lines) <= 1:
            return []
        for i in xrange(0,len(lines)):
            if lines[i].startswith(" "):
                continue
            similarAcordaoId = lines[i].replace(' PROCESSO ELETRÔNICO'.decode("utf8"),"").strip()
            similarAcordaoId = similarAcordaoId.replace(' ACÓRDÃO ELETRÔNICO'.decode("utf8"),"").strip()
            similarAcordaoId = similarAcordaoId.replace('-'," ").strip()
            dataJulg = orgaoJulg = relator = ""
            if len(lines) > i+1:
                dataJulg  = self.getMatchText( lines[i+1], r".*(?:JULG|ANO)-([\d\-]+).*") 
                ufShort   = self.getMatchText( lines[i+1], r".*UF-(\w\w).*") 
                orgaoJulg = self.getMatchText( lines[i+1], r".*TURMA-([\w\d]+).*") 
                relator   = self.getMatchText( lines[i+1], r".*M[Ii][Nn][-. ]+([^\.]+)")
                relator   = relator.replace(" N", "").strip()
                if not dataJulg and not ufShort and not relator:
                    print "doesn't match"
                    print( lines[i:i+3])
                    continue
                dataJulg = dataJulg.split("-")
                if len(dataJulg) > 1:
                    dataJulg = datetime( int(dataJulg[2]), int(dataJulg[1]), int(dataJulg[0]))
            similarAcordao = {"acordaoId": similarAcordaoId, "localSigla": ufShort, "dataJulg":dataJulg, "relator":relator, "orgaoJulg":orgaoJulg}
            similar.append(dict(similarAcordao))
        return( similar)


    def printLaw( self, law):
        print '-------------------------------------------------------------'
        print "sigla: "+ law["sigla"]
        print "desc: "+ law["descricao"]
        print "tipo: "+ law["tipo"]
        print "ano: "+ law["ano"]
        print "artigos: "
        for i,a in enumerate(law["artigos"]):
            print str(i) +": "+ a
        print '-------------------------------------------------------------'
