# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from stf.items import StfItem
from stf.items import StfLawItem
import re
import time
from datetime import datetime, timedelta
from scrapy.http import Request

class STFSpider(BaseSpider):

    name = 'stf'

    def __init__ ( self, iDate, fDate, page, index):
        self.domain = 'stf.jus.br'
        self.index  = self.fIndex = int(index)
        self.iDate  = iDate
        self.fDate  = fDate
        self.page   = int(page)
        self.start_urls = [ self.urlPage( page) ]

    def parse( self, response):
        npagesFound = 0
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divNaoImprimir"][2]'+
            '/table[1]/tr/td[2]/text()').extract()
        r = re.search(r"([0-9]+)", str(body))
        if r:
            npagesFound = int(r.group(1))/10+1
        for p in range(self.page, npagesFound+1):
            yield Request( self.urlPage( p), callback = self.parsePage)

    def parsePage( self, response ):
        unicode(response.body.decode(response.encoding)).encode('utf-8')
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divImpressao"]'+
            '/div[@class="abasAcompanhamento"]'+
            '/div[@class="processosJurisprudenciaAcordaos"]'
        )
        possHeaders = [
            'Parte',   
            'Decis',     # strong/p/strong/text() sec strong/p
            'Indexa',   # p/strong/text() sec next pre
            'Legisla',  # p/strong/text() sec next pre
            'Observa',  # p/strong/text() sec next pre
	    'Acórdãos no mesmo'.decode("utf-8"),
            'Doutrina'    # p/strong/text() sec next pre
        ]
        for doc in body:
            yield self.parseDoc( doc, possHeaders)

    def parseDoc( self, doc, possHeaders):
        self.fIndex += 1
        title = doc.xpath('p[1]/strong/text()').extract()
        acordaoId = self.getMatchText( title[0], '\s*([^\/]+).*')
        acordaoId = acordaoId.replace('-',' ').upper().strip()
        ufShort = self.getMatchText( title[0], '.*/\s*(\w*).*').upper().strip()
        uf = self.parseItem( self.getMatchText( title[0], '.*\/.*-\s*(.*)')).upper().strip()
        relator = self.parseItem( self.getMatchText( title[7], '\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)')).upper().strip()
        dataJulg = orgaoJulg =''
        for line in title[1:]:
            line = line.replace('&nbsp', '')
            line = self.parseItem( line)
            if line.startswith('Julgamento'):
                julgLine = re.match('Julgamento:\s*(\d{2})\/(\d{2})\/(\d{4})\s*.* Julgador:\s*(.*)', line)
                dataJulg = datetime( int(julgLine.group(3)), int(julgLine.group(2)), int(julgLine.group(1)))
                orgaoJulg = julgLine.group(4)
                break
        publicacao  = self.parseItem( doc.xpath('pre[1]/text()').extract()[0])
        ementa      = self.parseItem( doc.xpath('strong[1]/p/text()').extract()[1])
        sectHeaders = doc.xpath('p/strong/text()').extract()[len(title)+1:-1]
        sectBody    = doc.xpath('pre/text()').extract()[1:]
        sections    = self.orderSections(  sectHeaders, sectBody, possHeaders)
        decision = laws = obs = doutrines = result =''
        quotes = tags = similarAcordaos = [] 
        partes    = self.parseItem( self.getFoundSection( 0, sections))
        decision  = self.parseItem( self.getFoundSection( 1, sections))
        tags      = self.parseItem( self.getFoundSection( 2, sections))
        laws      = self.getLaws( self.getFoundSection( 3, sections))
        obs       = self.parseItem( self.getFoundSection( 4, sections))
        similarAcordaos = self.getSimilarAcordaos( self.getFoundSection( 5, sections))
        doutrines = self.parseItem( self.getFoundSection( 6, sections))
        if tags:
            tags = re.split(r'[\n,\-.]+', tags)
            for j in range( len(tags)):
                tags[j] = tags[j].strip()
            tags = filter(None, tags)
        if obs:
            quotes = self.getAcordaosQuotes( obs)
        item = StfItem(
            acordaoId   = acordaoId,
            localSigla  = ufShort,
            local       = uf,
            #publicacao  = publicacao,
            dataJulg    = dataJulg,
            orgaoJulg   = orgaoJulg,
            partes      = partes,
            relator     = relator,
            ementa      = ementa,
            decisao     = decision,
            citacoes    = quotes,
            legislacao  = laws,
            doutrinas   = doutrines,
            observacao  = obs, 
            tags        = tags, 
	        acordaosSimilares = similarAcordaos,
            tribunal    = "stf",
            index       = self.fIndex
        )
        return item
    
    def urlPage( self, n):
        return (
               'http://www.stf.jus.br/portal/jurisprudencia/listarJurisprudencia.asp?'+
               's1=%28%40JULG+%3E%3D+'+
                self.iDate +                 
               '%29%28%40JULG+%3C%3D+'+
                self.fDate +                 
               '%29'+
               '&pagina='+ str(n) +
               '&base=baseAcordaos')

    def parseItem( self, text ):
        text = text.replace("\r\n", ' ')
        text = text.replace("\n", ' ')
        text = text.strip()
        return text

    def orderSections( self, sectHeaders, sectBody, possHeaders):
        sections = {}
        for i,ph in enumerate(possHeaders):
            for j, sh in enumerate(sectHeaders):
                if (sh.startswith( ph)):
                    sections[i] = sectBody[j]
                    break
        return sections

    def getAcordaosQuotes( self, txt):
        quotes = []
        data = re.search(("Acórdão(?:\(?s\)?)? citado(?:\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])").decode("utf-8"), txt)
        if data:
            data = (data.group(1))
            data = re.split('[;,.()]', data)
            for q in data:
                q = re.match("[\s-]*([a-zA-Z]{2,}[ -]\d+[ -][a-zA-Z\- \d]*)\s*", q)
		if q:
		    q = q.group(1)
                    q = q.replace('-', ' ')
                    q = q.strip().upper()
                    quotes.append( q) 
        return quotes

    def getFoundSection( self, n, sections):
        if n in sections.keys():
            return sections[n]
        else:
            return ''

    def getSimilarAcordaos( self, raw):
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
                if not dataJulg or not ufShort or not relator:
                    print "doesn't match"
                    print( lines[i:i+3])
                    continue
                dataJulg = dataJulg.split("-")
                if len(dataJulg) > 1:
                    dataJulg = datetime( int(dataJulg[2]), int(dataJulg[1]), int(dataJulg[0]))
            similarAcordao = {"acordaoId": similarAcordaoId, "localSigla": ufShort, "dataJulg":dataJulg, "relator":relator, "orgaoJulg":orgaoJulg}
            similar.append(dict(similarAcordao))
        return( similar)

    def getLaws( self, raw):    
        laws = []
        law = {} 
        references ="" 
        lines = raw.split("\n")
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

    def printItem( self, item):
        print '-------------------------------------------------------------'
        print 'relator:\n'+item['relator']
        print '\nId:\n'+item['acordaoId']
        print '\nlocal:\n'+item['local']
        print '\ndataJulg:\n'+item['dataJulg']
#        print '\norgaoJulg:\n'+item['orgaoJulg']
#        print '\npublic:\n'+item.publicacao
        print '\npartes:\n'+item['partes']
        print '\nementa:\n'+item['ementa']
        print '\ndecisao:\n'+item['decisao']
        print '\nindexacao:\n'
        print item['tags']
        print '\nleis:\n'+item['legislacao']
        print '\ndoutrinas:\n'+item['doutrinas']
        print '\nobs:\n'+item['observacao']
#        print '\nresult:\n'+result
        print '\n\nquotes:\n'
        print item['citacoes']
        print '-------------------------------------------------------------'
 
    def getMatchText( self, text, regexExp):
        match = re.match( regexExp, text)
        if  match == None:
        #    print 'err getting '+ regexExp
         #   print 'from: '+ text
          #  print 'index: '+ str( self.fIndex) 
            return ''
        else:
            return (match.group(1)).strip()



        
         
