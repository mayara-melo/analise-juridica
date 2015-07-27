# -*- coding: utf-8 -*-

from AcordaoParser import AcordaoParser

#from stf.items import StfLawItem
import re
#import time
from datetime import datetime, timedelta

class STFParser( AcordaoParser):

    def normalizeId( self, Id):
        acNo = self.getMatchText( Id, '[A-Z]+\s+(\d+)\s*.*')
        typeInv = Id.replace( acNo, ' ').upper().strip()
        idList = typeInv.split()
        Id = ' '.join( reversed(idList))
        return Id +' '+ acNo

    def parseId( self, text):
        idRaw = self.getMatchText( text, '\s*([^\/]+).*').upper()
        idRaw = idRaw.replace('-', ' ').strip()
        return self.normalizeId( idRaw)

    def parseType( self, idNormalized):
        acNo = self.getMatchText( idNormalized, '[A-Z]+(\s+\d+)')
        return idNormalized.replace( acNo, '')

    def parseUfShort( self, text):
        return self.getMatchText( text, '.*/\s*(\w*).*').upper().strip()

    def parseRelator( self, text):
        return self.getMatchText( text, '\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)').upper().strip()

    def parseDataJulgamento( self, text):
        text = text.replace('&nbsp', '').strip()
        date = re.search('Julgamento:\s*(\d{2})\/(\d{2})\/(\d{4})', text)
        if date:
            return datetime( int(date.group(3)), int(date.group(2)), int(date.group(1)))
        return ''

    def parseDataPublicacao( self, text):
        text = text.replace('&nbsp', '').strip()
        date = re.search('PUBLIC (\d+)[-\/](\d+)[-\/](\d+)', text)
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
        data = re.search(("[Aa]córdão(?:\s*\(?s\)?)? citado(?:\s*\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])").decode("utf-8"), txt)
        if data:
            data = (data.group(1))
            data = re.split('[;,.()]', data)
            for q in data:
                q = q.strip()
                q = re.match("([a-zA-Z]{2,}[ -]\d+[a-zA-Z]*).*", q)
                if q:
                    q = q.group(1)
                    q = q.replace('-', ' ')
                    q = q.strip().upper()
                    quotes.append( self.normalizeId( q))
        return quotes
 
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
            similarAcordaoId = self.normalizeId( similarAcordaoId)
            dataJulg = orgaoJulg = relator = ""
            if len(lines) > i+1:
                dataJulg  = self.getMatchText( lines[i+1], r".*(?:JULG|ANO)-([\d\-]+).*") 
                ufShort   = self.getMatchText( lines[i+1], r".*UF-(\w\w).*") 
                orgaoJulg = self.getMatchText( lines[i+1], r".*TURMA-([\w\d]+).*") 
                relator   = self.getMatchText( lines[i+1], r".*M[Ii][Nn][-. ]+([^\.]+)")
                relator   = relator.replace(" N", "").strip()
#                if not dataJulg and not ufShort and not relator:
 #                   print "doesn't match"
  #                  print( lines[i:i+3])
   #                 continue
                dataJulg = dataJulg.split("-")
                if len(dataJulg) > 1:
                    dataJulg = datetime( int(dataJulg[2]), int(dataJulg[1]), int(dataJulg[0]))
            similarAc = {"acordaoId": similarAcordaoId, "localSigla": ufShort, "dataJulg":dataJulg, "relator":relator, "orgaoJulg":orgaoJulg}
            similar.append(dict(similarAc))
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

