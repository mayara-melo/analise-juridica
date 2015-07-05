# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from stf.items import StfItem
from stf.items import StfLawItem
import re
import time
from datetime import datetime, timedelta
from scrapy.http import Request
from STFParser import STFParser

class STFSpider(BaseSpider):

    name = 'stf'

    def __init__ ( self, iDate, fDate, page, index):
        self.domain = 'stf.jus.br'
        self.index  = self.fIndex = int(index)
        self.iDate  = iDate
        self.fDate  = fDate
        self.page   = int(page)
        self.start_urls = [ self.urlPage( page) ]
        self.parser = STFParser()

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
        for doc in body:
            yield self.parseDoc( doc)

    def parseDoc( self, doc):
        parser = self.parser
        self.fIndex += 1
        title = doc.xpath('p[1]/strong/text()').extract()
        acordaoId = parser.parseId( title[0])
        ufShort   = parser.parseUfShort( title[0])
        uf        = parser.parseUf( title[0]) 
        relator   = parser.parseRelator( title[7])
        dataJulg  = parser.parseDataJulgamento( ''.join(title[1:]))
        orgaoJulg = parser.parseOrgaoJulgador( ''.join(title[1:]))
#        print orgaoJulg

        publicacao  = doc.xpath('pre[1]/text()').extract()[0].strip()
        ementa      = doc.xpath('strong[1]/p/text()').extract()[1].strip()

        headers = doc.xpath('p/strong/text()').extract()[len(title)+1:-1]
        bodies  = doc.xpath('pre/text()').extract()[1:]
        sections = zip( headers, bodies)

        partes     = self.getSectionBodyByHeader( "Parte", sections)
        decision   = self.getSectionBodyByHeader( "Decis", sections)
        tagsRaw    = self.getSectionBodyByHeader( "Index", sections)
        lawsRaw    = self.getSectionBodyByHeader( "Legisla", sections)
        obs        = self.getSectionBodyByHeader( "Observ", sections)
        similarRaw = self.getSectionBodyByHeader( "Acórdaos no mesmo".decode("utf8"), sections)
        doutrines  = self.getSectionBodyByHeader( "Doutrinas", sections)

        tags   = parser.parseTags( tagsRaw)
        quotes = parser.parseAcordaosQuotes( obs)
        laws   = parser.parseLaws( lawsRaw)
        similarAcordaos = parser.parseSimilarAcordaos( similarRaw)

        item = StfItem(
            acordaoId   = acordaoId,
            localSigla  = ufShort,
            local       = uf,
            publicacao  = publicacao,
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

    def getSectionBodyByHeader( self, header, sections):
        for s in sections:
            if s[0].startswith( header):
                return s[1]
        return ''

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
