
import re
from datetime import datetime, timedelta

class AcordaoParser():

    abbreviationsTable = {
        "AGTE":   "agravante",
        "AGD":    "agravado",
        "ADVD":   "advogado",
        "ADV":    "advogado",
        "PACTE":  "paciente",
        "COATOR": "coator",
        "IMPTE":  "IMPTES"
    }
    
    def extendAbv( self, abv):
        word = re.sub("\(.*\)", '', abv)
        word = word.replace('.' , '')
        word = re.sub(r'^.*((as?)|(os?))$', '', word, flags=re.IGNORECASE)
        word = self.abbreviationsTable.get( word, abv) 
        return word
        
    def parseUfShort( self, text):
        return self.getMatchText( text, '.*/\s*(\w*).*').upper().strip()
        
    def parseUf( self, text):
        return self.getMatchText( text, '.*\/.*-\s*(.*)').upper().strip()

    def parseRelator( self, text):
        return self.getMatchText( text, '\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)').upper().strip()

    def parseId( self, text):
        idRaw = self.getMatchText( text, '\s*([^\/]+).*')
        return idRaw.replace('-',' ').upper().strip()

    def parseTags( self, text):
        if text:
            tags = re.split(r'[\n,\-.]+', text)
            for j in range( len(tags)):
                tags[j] = tags[j].upper().strip()
            return filter(None, tags)
        return []

    def parsePartes( self, text):
        partes = []
        lines = text.split('\n')
        for l in lines:
            if l.strip() and l.startswith(' '):
                partes[-1] = partes[-1]+ " "+l.strip()
            else:
                partes.append( l)
        partesDicts = []
        partes = filter( None, partes)
        for l in partes:
            temp = l.split(':')
            t = temp[0].strip()
            n = temp[1].strip()
            tipo = self.extendAbv( t)
            nome = re.sub('\s+',' ', n).strip()
            d = dict( { tipo: nome})
            partesDicts.append( d)
        return partesDicts

    def getMatchText( self, text, regexExp):
        match = re.match( regexExp, text)
        if  match == None:
            return ''
        else:
            return (match.group(1)).strip()


