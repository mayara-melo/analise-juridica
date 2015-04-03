# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser
from stj.items import StjItem
import urlparse
import re
from scrapy.shell import inspect_response
from datetime import datetime, timedelta
import time

class STJSpider(BaseSpider):

    name = 'stj'
    
    def nextDay( self, date):
        nextDay = datetime( int(date[0:4]), int(date[4:6]), int(date[6:8]))
        nextDay += timedelta( days=1)
        d = str(nextDay.day).zfill(2)
        m = str(nextDay.month).zfill(2)
        y = str(nextDay.year)
        return y+m+d
    
    def getParametersFromFile( self):
        print 'getting initial date and num previous acordaos from file'
        file = open("../update_settings", 'r')
        prevIndex = file.readline()
        prevFinalDate = file.readline()
        if prevIndex and prevFinalDate:
            self.iIndex = int( prevIndex) +1
            self.iDate = self.nextDay( str( prevFinalDate))
        else:
            print 'cannot read settings file'

    def saveSearchInfo( self):
        print 'saving search parameters on file update_settings'
        file = open("../update_settings", 'w')
        file.write( str(self.fIndex-1)+'\n')
        file.write( self.fDate +'\n')
        file.write( str(self.iIndex))
        file.close()

    def __init__ ( self, iDate, fDate, update):
        self.domain = 'stj.jus.br'
        self.start_urls = ["http://www.stj.jus.br/SCON/"]
        self.iDate = str(iDate).zfill(5)
        self.fDate = str(fDate).zfill(5)
        self.iIndex = 1
        if int(update) == 1:
            self.getParametersFromFile()
        self.fIndex = self.iIndex
        print 'starting to scrape from index '+ str(self.iIndex)
        print 'Acordaos from '+self.iDate+' to '+self.fDate
        print "\n\n\n"

    def parse(self, response):
        yield FormRequest.from_response(
            response,
            formname='frmConsulta',
            formdata={'livre':'(@DTDE >="'+self.iDate+'") E (@DTDE <="'+self.fDate+'")', 'b':'ACOR'},
            callback=self.parsePage
        )

    def parseDoc( self, doc):
        relator = dataJulg = dataPublic = ementa = decisao = notas = leis =''
        citacoes = []
        possSection = [
            'Data do Julg',           #0
            'Data da Publ',           #1
            'Ementa',                 #2
            'Ac',                #3
            'Refer',                  #4
            'Veja'                    #5
        ]
        sectionsSel =  doc.xpath('.//div[@class="paragrafoBRS"]')
        # Permanent order sections
        processo   = self.extractText( sectionsSel[0], './div[@class="docTexto docRepetitivo"]/text()')
        acordaoId  = self.getReversedId( self.getMatchText( processo, r"\s*([^\/]*).*"))
        localSigla = self.getMatchText( processo, r"[^\/]*\/\s*(..).*")
        relator    = self.extractText( sectionsSel[1], './pre/text()')
        relator    = self.getMatchText( relator, r"M[A-Za-z\)\(:.]*\W*([^\(]*).*")
 
        # Facultative/unordered sections
        sections = self.orderSections( sectionsSel, possSection)
        dataJulg = self.extractText( sections[0], './pre/span/text()' )
        dataJulg = datetime( int(self.getMatchText( dataJulg, r"\d\d\/\d\d\/(\d{4})")),
                             int(self.getMatchText( dataJulg, r"\d\d\/(\d\d)\/\d{4}")),
                             int(self.getMatchText( dataJulg, r"(\d\d)\/\d\d\/\d{4}"))
                            )
        if 1 in sections:
            dataPublic = sections[1].xpath( './pre/text()').extract()
            dataPublic = re.search(r"(\d{2})\/(\d{2})\/(\d{4})" ,self.parseItem((''.join(dataPublic))))
            dataPublic = datetime( int(dataPublic.group(3)), int(dataPublic.group(2)), int(dataPublic.group(1)))
        ementa = self.extractText( sections[2], './pre/text()')
        decisao =  self.extractText( sections[3], './pre/text()')
        if 4 in sections:
            leis = self.getLaws( sections[4])
        if 5 in sections:
            citacoes = self.getQuotations( sections[5])
        return StjItem(
                acordaoId   = acordaoId,
                localSigla  = localSigla,
                dataPublic  = dataPublic,
                dataJulg    = dataJulg,
                relator     = relator,
                ementa      = ementa,
                decisao     = decisao,
                citacoes    = citacoes,
                legislacao  = leis,
                index       = self.fIndex,
                tribunal    = 'stj'
        )

    def parseItem( self, text):
        text = text.replace("\r\n", ' ')
        text = text.replace("\n", ' ')
        text = text.strip()
        return text

    def orderSections( self, selectors, possHeader):
        sections = {}
        for sec in selectors:
            header = self.parseItem( self.extractText( sec, './h4/text()'))
            for i, h in enumerate( possHeader):
                if( header.startswith( h)):
                    sections[i] = sec
                    break
        return sections

    def extractText( self, selector, xpath):     
        text = selector.xpath( xpath).extract()[0]
        if text == None:
            print 'err getting xpath: ' +xpath+'from selector '
            print selector
            print 'index: '+ str( self.fIndex) 
            return ''
        else:
            return self.parseItem( text)

    def getMatchText( self, text, regexExp):
        match = re.match( regexExp, text)
        if  match == None:
            print 'err getting '+ regexExp
            print 'from: '+ text
            print 'index: '+ str( self.fIndex) 
            return ''
        else:
            return (match.group(1)).strip()

    def getReversedId( self, txt):
        acId = re.split( r" [nN][oOaA][sS]? ", txt.strip())
        a = ''
        for i in reversed(acId):
            a = a + i +' '
        return a.upper().strip()

    def getQuotations( self, sel):
        quotes = []
        linkedQuotes = sel.xpath('./pre/a/text()').extract()
        for l in linkedQuotes:
            quotes.append( self.getReversedId( l.upper()))
        otherQuotes = sel.xpath( "./pre/text()").extract()
        for q in otherQuotes:
            q = q.upper()
            m = re.match( r"\s*(?:ST[FJ][\s-]*)?([A-Z -]+[\d]+)[-]?.*", q)
            if m:
                q = m.group(1).strip()
                quotes.append( q)
        return quotes
        
    def getLaws( self, sel):    
        laws = []
        linked = sel.xpath('./pre/a/text()').extract()
        for l in linked:
            print l
            l = re.match( r"\s*LEG:FED ...:(\d+)(?: ANO:\d+)?", l)
            if l:
                print "found "+ l.group(1)
                laws.append( l.group(1).upper())
        others = sel.xpath( "./pre/text()").extract()
#        print "others: "
 #       print others
  #      print "--------"
        return laws
    
    def parsePage( self, response):
        unicode(response.body.decode(response.encoding)).encode('utf-8')
        sel = Selector(response)
        doclist = sel.xpath(
            '/html/body/div[@id="divprincipal"]'+
            '/div[@class="minwidth"]'+
            '/div[@id="idInternetBlocoEmpacotador"]'+
            '/div[@class="incenter_interno"]'+
            '/div[@id="idDivContainer"]'+
            '/div[@id="idAreaBlocoExterno"]'+
            '/div[@id="idArea"]'+
            '/div[@id="corpopaginajurisprudencia"]'+
            '/div[@id="listadocumentos"]'+
            '/div[@style="position: relative;"]')
        for doc in doclist:
            yield self.parseDoc( doc)
            self.fIndex = self.fIndex + 1
        nextPage = sel.xpath('//*[@id="navegacao"]/a/img[@src="/recursos/imagens/tocn.gif"]')
        if nextPage:
            yield Request( urlparse.urljoin('http://www.stj.jus.br/',
                           self.extractText( nextPage,'../@href')),
                           callback=self.parsePage )
        else:
            self.saveSearchInfo()
