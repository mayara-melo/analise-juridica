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
            return match.group(1).upper().strip()
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

 
    def parseLawReferences( self, text):
        refs = re.split("((?:CAP|INC|PAR|LET|ART)-[\w\d]+)\s*", text)
        ref = {}
        lawRefs = []
        nCap = nArt = nPar = nInc = nAli = 0
        refs = filter(None, refs)
        for r in refs:
            r = r.strip()
            if r.startswith("CAP"):
                if nCap:
                    print "CAPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
                    lawRefs.append( dict(ref))
                    ref = {}
                    nArt = nInc = nPar = nLet = 0
                ref["capitulo"] = self.getMatchText( r, "CAP[- ]+([\d\w]+).*")
                nCap = 1
            elif r.startswith("ART"):
                if nArt:
                    lawRefs.append( dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    ref.pop("paragrafo", None)
                    nInc = nPar = nLet = 0
                ref["artigo"] = self.getMatchText( r, "ART[- ]+([\d\w]+).*")
                nArt = 1
            elif r.startswith("PAR"):
                if nPar or nAli:
                    lawRefs.append( dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    nInc = nAli = 0
                ref["paragrafo"] = self.getMatchText( r, "PAR[- ]+([\d\w]+)")
                nPar = 1
            elif r.startswith("INC"):
                if nInc or nAli:
                    lawRefs.append( dict(ref))
                    ref.pop("alinea", None)
                    nAli = 0
                ref["inciso"] = self.getMatchText( r, "INC[- ]+([\d\w]+)")
                nInc = 1
            elif r.startswith("LET"):
                if nAli:
                    lawRefs.append( dict(ref))
                nAli = 1
                ref["alinea"] = self.getMatchText( r, "LET[- ]+([\d\w]+)")
            elif r.startswith("\"CAPUT"):
                ref["caput"] = 1  
                lawRefs.append( dict(ref))
                nAli = nInc = nPar = nLet = 0
                ref.pop("inciso", None)
                ref.pop("alinea", None)
                ref.pop("caput", None)
                ref.pop("paragrafo", None)
            else:
                print r
        if ref:
            lawRefs.append( dict(ref))
        return lawRefs 

    def parseLaws( self, text):    
        laws = []
        law = {}
        refs = {}
        lawLines = []
        lines = text.split("\n")
        for l in lines:
            l = l.encode("utf-8").upper()
            if l.startswith("LEG"):
                if lawLines:
                    if re.match( "\s*(PAR|INC|ART|CAP|LET).*", lawLines[-1]):
                        law["descricao"] = ""
                    else:
                        law["descricao"] = lawLines.pop().split()
                    law["refs"] = self.parseLawReferences( ''.join( lawLines))
                    if law:
                        self.printLaw( law)
                    laws.append( law)
                    law = {}
                    lawLines = [] 
                law["sigla"] = self.getMatchText( l, r"\s*LEG-\w+\s+([^\s]+).*")
                law["tipo"] = self.getMatchText( l, r"\s*LEG-(\w+).*")
                law["ano"] = self.getMatchText( l, r".*ANO[-:](\d+).*")
            else:
                lawLines.append( " "+l.strip())
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
        print "refs: "
 #       print law["refs"]
        for i,a in enumerate(law["refs"]):
            print a
        print '-------------------------------------------------------------'

