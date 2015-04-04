# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser
from stj.items import StjItem
from stj.items import StjLawItem
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
        relator = dataJulg = dataPublic = ementa = decisao = ''
        leis = []
        citacoes = []
        notas = []
        possSection = [
            'Data do Julg',           #0
            'Data da Publ',           #1
            'Ementa',                 #2
            'Ac',                     #3
            'Notas',                  #4
            'Refer',                  #5
            'Veja',                    #6
            'Doutrina'                #7
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
            notasNonlinked = sections[4].xpath( './pre/text()').extract()
            notasLink = sections[4].xpath( './pre/a/text()').extract()
            for a in notasNonlinked:
                notas.append( a)
                if len( notasLink):
                    notas.append( notasLink.pop(0))
            notas = self.parseItem("".join( notas))
        if 5 in sections:
            leis = self.getLaws( sections[5])
        if 6 in sections:
            citacoes = self.getQuotations( sections[6])
        if 7 in sections:
            doutrinas = self.parseItem( "".join(sections[7].xpath( "./pre/text()").extract()))
            print doutrinas
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
                notas       = notas,
                tribunal    = 'stj'
        )

    def parseItem( self, text):
        text = text.replace("\r\n", ' ')
        text = text.replace("\n", ' ')
        text = text.strip()
        return text

    def orderSections( self, selectors, possHeader):
        sections = {}
        ignoreSections = ["Processo", "Relator(a)", "Órgao Julgador"]
        for sec in selectors:
            header = self.parseItem( self.extractText( sec, './h4/text()'))
            found = 0
            for i, h in enumerate( possHeader):
                if( header.startswith( h)):
                    sections[i] = sec
                    found=1
                    break
        #    if not found and header not in ignoreSections:
         #       print header
          #      print "------------------------"
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
        #    print 'err getting '+ regexExp
         #   print 'from: '+ text
          #  print 'index: '+ str( self.fIndex) 
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
        possQuotes =[]
        quotes = []
        linkedQuotes = sel.xpath('./pre/a/text()').extract()
        for l in linkedQuotes:
            quotes.append( self.getReversedId( l.upper()))
        otherQuotes = sel.xpath( "./pre/text()").extract()
        otherQuotes.append("dummy")
        for line in otherQuotes:
            l = re.split(r"[\n,]", line)
            possQuotes.extend( l)
        for q in possQuotes:
            m = self.getMatchText( q.upper(), r"(?:\s*ST[FJ] - )?\s*([A-Z ]+\d+\/?).*")
            if m and not m.endswith("/"):
                quotes.append( m)
        return quotes
        
    def getLaws( self, sel):    
        laws = []
        possLaws = []
        raw = sel.xpath('./pre/a/text()').extract()
        others = ( sel.xpath('./pre/text()').extract())
        raw.extend( others)
        for line in raw:
            l = line.split("\n")
            possLaws.extend( l)
        for l in possLaws:
            l = l.upper()
            lawType = self.getMatchText( l, r"(?:[A-Z:-]+ )?(\w+)[:-][\d\*]+(?:\s*ANO:\d+)?.*")
            lawNum  = self.getMatchText( l, r"(?:[A-Z:-]+ )?\w+[:-](\d+)(?:\s*ANO:\d+)?.*")
            lawYear = self.getMatchText( l, r".*ANO:(\d+).*")
            if lawNum or lawType:
                lawItem = StjLawItem( tipo = lawType, numero = lawNum, ano = lawYear)
                laws.append( dict(lawItem))
            else:
                lawType = self.getMatchText( l, r"\s*[\*]+\s*([A-Z]+)[- ]+.*")  
#                lawName = self.getMatchText( l, r"\s*[\*]+\s*[A-Z]+[- ]+\d*([\w ]+)").lower.strip()
                lawYear = self.getMatchText( l, r"\s*[\*]+\s*[A-Z]+[- ]+(\d+).*")
                lawNum = ""
                if lawType and lawYear:
                    if len(lawYear) == 2:
                        if int(lawYear) > 15:
                            lawYear = "19" + lawYear 
                        else:
                            lawYear = "20" + lawYear
#                    print l.encode("utf-8")
 #                   print "foundn: "+ lawType
  #                  print "founnn: "+ str(lawYear)
                    lawItem = StjLawItem( tipo = lawType, numero = lawNum, ano = lawYear)
                    laws.append( dict(lawItem))
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
