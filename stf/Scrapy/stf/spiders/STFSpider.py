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
            'Doutrina'    # p/strong/text() sec next pre
        ]
        for doc in body:
            self.parseDoc( doc, possHeaders)

    def parseDoc( self, doc, possHeaders):
        self.fIndex += 1
        title = doc.xpath('p[1]/strong/text()').extract()
        titleLine = re.match('\s*([^\/]+)\/\s*(\w*)\s*-\s*(.*).*', title[0])
        acordaoId = (titleLine.group(1).replace('-',' ')).strip()
        ufShort = self.parseItem( titleLine.group(2))
        uf = self.parseItem( titleLine.group(3))
        relator = self.parseItem( re.match('\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)', title[7] ).group(1))
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
        quotes = tags = [] 
        partes    = self.parseItem( self.getFoundSection( 0, sections))
        decision  = self.parseItem( self.getFoundSection( 1, sections))
        tags      = self.parseItem( self.getFoundSection( 2, sections))
        if 3 in sections:
            laws  = self.getLaws( sections[3])
        obs       = self.parseItem( self.getFoundSection( 4, sections))
        doutrines = self.parseItem( self.getFoundSection( 5, sections))
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
#           publicacao  = publicacao,
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
        data = re.search(r"Acórdão(?:\(?s\)?)? citado(?:\(?s\)?)?\s*:\s*([^:]*)(?=\.[^:])", txt)
        if data:
            data = (data.group(1))
            data = re.split('[;,.()]', data)
            for q in data:
                if re.search(r'\d+', q):
                    q = q.replace('-', ' ')
                    q = q.strip()
                    quotes.append( q) 
                else:
                    print "raw"
                    print data
                    print "-------------"
                    print "not found"
                    print q.encode("utf-8")
                    print "-------------"
        return quotes

#    def getResult( self, txt):
#        result = ''
#        print txt
#        txt = txt.split('\r\n')
#        print '------------------'
#        dataHeaders = [
#            'Vota',
#            'Resultado:',
#            'Veja:',
#            ''
#        ]
#        temp = re.search('Resultado:\s*(.*)\r\n', txt[0])
#        if temp:
#            print temp.group(1)
#        
    #   temp = re.search('Resultado:\s*(.*)', txt)
   #     if temp:
  #          temp = a.group(1)
 #           temp = re.search('(.*)(Ac.rd.o[s]? citado)', temp)
 #       if temp:
  #          temp
   #         print result

    def getFoundSection( self, n, sections):
        if n in sections.keys():
            return sections[n]
        else:
            return ''

    def getLaws( self, raw):    
        laws = []
        lines = raw.split("\n")
        for l in lines:
            l = l.encode("utf-8").upper()
            lawType = self.getMatchText( l, r"\s*(?:LEG-...)\s*(\w+)[:-]?[\d+\*]?(?:\s*ANO:\d+)?.*")
            lawNum  = self.getMatchText( l, r"\s*(?:LEG-...)\s*\w+[:-](\d+)\s*(?:\s*ANO:\d+)?.*")
            if lawNum or lawType:
                lawYear = self.getMatchText( l, r".*ANO[-:](\d+).*")
                lawItem = StfLawItem( tipo = lawType, numero = lawNum, ano = lawYear)
                laws.append( dict(lawItem))
#                print l.encode("utf-8")
 #               print "Type: "+ lawType
#              print "num: "+ lawNum
 #               print "ano : "+ lawYear
  #              print "---------------------------------"
            else:
                lawType = self.getMatchText( l, r"\s*([A-Z]+)\-\d+[\w^\- ]+")  
                if lawType == "ART" or lawType =="PAR" or lawType == "INC":
                    continue;
                lawYear = self.getMatchText( l, r"\s*[A-Z]+\-(\d+)[\w^\- ]+")  
                lawNum = ""
                if lawType:
                    if len(lawYear) == 2:
                        if int(lawYear) > 15:
                            lawYear = "19"+ lawYear
                        else:
                            lawYear = "20"+ lawYear
#                    print l
 #                   print "foundn2Type: "+ lawType
#                    print "founnn2ano : "+ lawYear
 #                   print "---------------------------------"
                    lawItem = StfLawItem( tipo = lawType, numero = lawNum, ano = lawYear)
                    laws.append( dict(lawItem))
                #else:
#                    print "----------not found-----------------------"
 #                   print l
  #                  print "---------------------------------"
        return laws
 
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


        
         
