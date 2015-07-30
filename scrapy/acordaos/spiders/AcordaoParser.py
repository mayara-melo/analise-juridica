import re

class AcordaoParser():
   
    def extendAbv( self, abv):
        abv = abv.replace('.', '').lower()
        abv = re.sub("\(.*\)", '', abv)
        word = re.sub(r'([ao]?s?)$', '', abv, flags=re.IGNORECASE)
        word = self.abbreviationsTable.get( word, abv)
        return word
        
    def parseUf( self, text):
        return self.getMatchText( text, '.*\/.*-\s*(.*)').upper().strip()

    def parseType( self, acordaoId):
        return re.sub( '\d+\s*', '', acordaoId).strip()

    def parseTags( self, text):
        tags = []
        if text:
            tagsRaw = re.split(r'[\n,\-.]+', text)
            for tag in tagsRaw:
                t = (re.sub('\s+', ' ', tag)).strip()
                tags.append( t.upper())
            return filter(None, tags)
        return []

    def parsePartes( self, text):
        partes = []
        lines = text.split('\n')
        for l in lines:
            if l.strip() and l.startswith(' ') and partes:
                partes[-1] = partes[-1]+ " "+l.strip()
            else:
                partes.append( l)
        partesDict ={} 
        partes = filter( None, partes)
        for l in partes:
#            temp = l.split(:)
            temp = re.split('[:;]', l)
            if len(temp) < 2:
#                print 'temp:'
#                print temp  
#                print 'parte:'  
#                print l  
#                print 'partes:'
#                print partes  
#                print '------'  
		continue
            t = temp[0].strip()
            n = temp[1].strip()
            tipo = self.extendAbv( t)
            nome = re.sub('\s+',' ', n).strip()
            if tipo in partesDict:
                partesDict[ tipo].append( nome)
            else: 
                partesDict[ tipo] = [nome]
        return dict(partesDict)

    def parseLawReferences( self, text):
        refs = re.split("((?:INC|PAR|LET|ART)[- :][\w\d]+)\s*", text)
        ref = {}
        lawRefs = []
        nCaputs = nArt = nPar = nInc = nAli = 0
        refs = filter(None, refs)
        for r in refs:
            r = r.strip()
            if r.startswith("ART"):
                if nArt or nCaputs:
                    lawRefs.append( dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    ref.pop("paragrafo", None)
                    ref.pop("caput", None)
                    nInc = nCaputs = nPar = nAli = 0
                ref["artigo"] = self.getMatchText( r, "ART[-: ]+(.+)")
                nArt = 1
            elif r.startswith("PAR"):
                if nPar or nAli or nCaputs:
                    lawRefs.append( dict(ref))
                    ref.pop("inciso", None)
                    ref.pop("alinea", None)
                    ref.pop("caput", None)
                    nInc = nAli = nCaputs = 0
                ref["paragrafo"] = self.getMatchText( r, "PAR[-: ]+(.+)")
                nPar = 1
            elif r.startswith("INC"):
                if nInc or nAli or nCaputs:
                    lawRefs.append( dict(ref))
                    ref.pop("alinea", None)
                    ref.pop("caput", None)
                    nAli = nCaputs = 0
                ref["inciso"] = self.getMatchText( r, "INC[- :]+(.+)")
                nInc = 1
            elif r.startswith("LET"):
                if nAli or nCaputs:
                    lawRefs.append( dict(ref))
                    ref.pop("caput", None)
                    nCaputs = 0
                nAli = 1
                ref["alinea"] = self.getMatchText( r, "LET[-: ]+(.+)")
            elif r.startswith("\"CAPUT"):
                ref["caput"] = 1  
                nAli = nInc = nPar = nLet = 0
                nCaputs = 1
                ref.pop("inciso", None)
                ref.pop("alinea", None)
                ref.pop("paragrafo", None)
        if ref:
            lawRefs.append( dict(ref))
        return lawRefs 

    def parseLawDescription( self, text):
        if re.match( "\s*(PAR|INC|ART|CAP|LET).*", text):
            return ""
        desc = re.sub("[\*]+", '', text)
        return desc.strip()
        
    def parseLaws( self, text):    
        laws = []
        law = {}
        refs = {}
        lawLines = []
        text = text.replace('\r', ' ')
        lines = text.split("\n")
        for l in lines:
            l = l.encode("utf-8").upper()
            if l.startswith("LEG"):
                if lawLines:
                    description = self.parseLawDescription( lawLines[-1])
                    if description:
                        law["descricao"] = description
                        lawLines.pop()
                    law["refs"] = self.parseLawReferences( ''.join( lawLines))
                laws.append( law)
                law = {}
                lawLines = [] 
                law["descricao"] = ""
                law["refs"] = []
                law["sigla"] = self.getMatchText( l, r"\s*LEG[-:]\w+\s+([^\s]+).*")
                law["tipo"] = self.getMatchText( l, r"\s*LEG[-:](\w+).*")
                law["ano"] = self.getMatchText( l, r".*ANO[-:](\d+).*")
            elif l.startswith('***'):
                law["descricao"] = l
            else:
                lawLines.append( " "+l.strip())
        #append last law
        if law:
            if lawLines:
                description = self.parseLawDescription( lawLines[-1])
                law["descricao"] = description
                if description:
                    lawLines.pop()
            law["refs"] = self.parseLawReferences( ''.join( lawLines))
            laws.append( law)
        return laws

    def getMatchText( self, text, regexExp):
        match = re.match( regexExp, text)
        if  match == None:
            return ''
        else:
            return (match.group(1)).strip()

    def removeExtraSpaces( self, text):
        return re.sub('\s+', ' ', text).strip()

    abbreviationsTable = {
        "advd":   "advogado",
        "adv":    "advogado",
        "impte":  "impetrante",
        "recte":  "recorrente",
        "proc":   "procurador",
        "relator": "relator",
        #acusante
        "agd":    "agravado",
        "agdv":   "agravado",
        "reqte":  "requerente",
        "reclte": "reclamante",
        "pacte":  "paciente",
        "impd":   "impetrado",
        "imptd":  "impetrado",
        "impt":   "impetrado",
        "embte":  "embargante",
        "intd":   "intimado",
        "coator": "coator",
        #acusado
        "agte":   "agravante",
        "recdo":  "recorrido",
        "recldo": "reclamado",
        "embd":   "embargado",
        "embgd":  "embargado",
        "autore": "autor"
    }
 
