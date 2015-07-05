
import re
from datetime import datetime, timedelta

class AcordaoParser():

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

    def getMatchText( self, text, regexExp):
        match = re.match( regexExp, text)
        if  match == None:
            return ''
        else:
            return (match.group(1)).strip()


