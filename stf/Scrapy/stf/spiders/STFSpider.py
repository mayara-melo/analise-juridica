# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spider import BaseSpider
import html2text
from stf.items import StfItem
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
            yield self.parseDoc( doc, possHeaders)

    def parseDoc( self, doc, possHeaders):
        self.fIndex += 1
        title = doc.xpath('p[1]/strong/text()').extract()
        titleLine = re.match('\s*([\w -]+)\/\s*(\w*)\s*-\s*(.*).*', title[0])
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
        publicacao  = self.parseItem( doc.xpath('pre[1]/text()').extract()[0]).strip()
        ementa      = self.parseItem( doc.xpath('strong[1]/p/text()').extract()[1]).strip()
        sectHeaders = doc.xpath('p/strong/text()').extract()[len(title)+1:-1]
        sectBody    = doc.xpath('pre/text()').extract()[1:]
        sections  = self.orderSections(  sectHeaders, sectBody, possHeaders)
        decision  = laws = obs = doutrines = result =''
        quotes = tags = [] 
        partes    = self.parseItem( self.getFoundSection( 0, sections)).strip()
        decision  = self.parseItem( self.getFoundSection( 1, sections)).strip()
        tags      = self.parseItem( self.getFoundSection( 2, sections)).strip()
        laws      = self.parseItem( self.getFoundSection( 3, sections)).strip()
        obs       = self.parseItem( self.getFoundSection( 4, sections)).strip()
        doutrines = self.parseItem( self.getFoundSection( 5, sections)).strip()
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
        text = html2text.html2text( text)
#        text = text.decode("iso-8859-1").encode('utf-8')
        text = text.encode("utf-8")
#        text = text.decode('iso-8859-1')
        text = text.replace('\\r', '')
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
 
        
         
