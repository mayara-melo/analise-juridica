# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
import html2text
import re

def findId( text):
    return text


class STFSpider(BaseSpider):

    name = 'stfSpider'

    def __init__ ( self, iDate, fDate, page, index):
        print 'INIT SPIDERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n\n\n\n\n\n\n\n\n\n'
        self.domain = 'stf.jus.br'
        self.index = int(index)
        #self.fIndex = int(index)
        self.start_urls = [
            'http://www.stf.jus.br/portal/jurisprudencia/listarJurisprudencia.asp?'+
            's1=%28%40JULG+%3E%3D+'+
             iDate +                 # data inicial
            '%29%28%40JULG+%3C%3D+'+
             fDate +                 # data final
            '%29'
            '&pagina='+page+
            '&base=baseAcordaos'
        ]
    
    def parseItem( self, item ):
        text = item.replace("&nbsp", '')
        return html2text.html2text( text)

    def orderSections( self, sectHeaders, sectBody, possHeaders):
        sections = {}
        for i,ph in enumerate(possHeaders):
            for j, sh in enumerate(sectHeaders):
                sh = self.parseItem( sh)
                if (sh.startswith( ph)):
                    sections[i] = sectBody[j]
                    break
        return sections

    def parseObservSection( self, sel):
        txt = self.parseItem(sel.extract())
        quotes = re.search("Ac.rd.os citados\s*:\s*([^\.]*)", txt)
        if quotes:
            quotes = (quotes.group(1)).split(', ')
#            map( replace(re.compile('[^\s]'), '')
            print quotes

        

    def parse( self, response ):
        print "\n\n\n\n"
        print 'parse method\n\n'
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
            title = doc.xpath('p[1]/strong/text()').extract()
            titleLine = re.match('\s*([\w -]+)\/\s([A-Za-z]{2}).*', title[0])
            acordaoId = self.parseItem( (titleLine.group(1)).replace('-',' '))
            uf = self.parseItem( titleLine.group(2))
            relator = self.parseItem( re.match('\s*Relator\(a\):.+[Mm][Ii][Nn].\s*([a-zA-Z ]+)', title[7] ).group(1))
            for dataElem in title:
                if dataElem.startswith('Julgamento'):
                    titleLine = re.match('\s*Julgamento:\s*([\d\/]+)\s*.*Julgador:\s*([\w ]+).*', self.parseItem(dataElem ))
                    dataJulg = titleLine.group(1)
                    orgaoJulg = titleLine.group(2)
                    break
            publicacao = self.parseItem( doc.xpath('pre[1]/text()').extract()[0])            
            partes = self.parseItem( doc.xpath('pre[2]/text()').extract()[0])            
            ementa = self.parseItem( doc.xpath('strong[1]/p/text()').extract()[1])

            sectHeaders = doc.xpath('p/strong').extract()[3:]
#            map(self.parseItem, docHeaders)
            sectBody = doc.xpath('pre')[2:]
#            map( self.parseItem, sectBody)
            possHeaders = [
                '**Decis',     # strong/p/strong/text() sec strong/p
                '**Indexa',   # p/strong/text() sec next pre
                '**Legisla',  # p/strong/text() sec next pre
                '**Observa',  # p/strong/text() sec next pre
                '**Doutrina'    # p/strong/text() sec next pre
            ]
            sections = {}                
            sections = self.orderSections(  sectHeaders, sectBody, possHeaders)
            decision = tags = laws = obs = doutrines = ''
            keys = sections.keys()
            if 0 in keys:
                decision = self.parseItem(sections[0].extract())
            if 1 in keys:
                tags = self.parseItem(sections[1].extract())
            if 2 in keys:
                laws = self.parseItem(sections[2].extract())
            if 3 in keys:
                obs = self.parseItem(sections[3].extract())
                self.parseObservSection( sections[3])
            if 4 in keys:
                doutrines = self.parseItem(sections[4].extract())
            print '-------------------------------------------------------------'
            print 'relator: '+relator
            print '\nId: '+acordaoId
            print '\nuf: '+uf
            print '\ndataJulg: '+dataJulg
            print '\norgaoJulg: '+orgaoJulg
            print '\npublic: '+publicacao
            print '\npartes: '+partes
            print '\nementa: '+ementa
            print '\ndecisao: '+decision
            print '\nindexacao: '+tags
            print '\nleis: '+laws
            print '\ndoutrinas: '+doutrines
            print '\nobs: '+obs
            print '\n'
            print '-------------------------------------------------------------'
#            yield StfItem(
#                acordaoId   = acordaoId,
#                uf          = uf,
#                publicacao  = publicacao,
#                dataJulg    = dataJulg,
#                relator     = relator,
#                ementa      = ementa,
#                decisao     = decisao,
#              #  citacoes    = citacoes,
#                filename    = 'stf'+str(self.fIndex).zfill(6)
# 
           # f = open( '../files/stf'+str(self.index).zfill(6)+'.xml', 'w' )
           # f.write(html2text.html2text( div ).encode('utf-8'))
           # self.index = self.index + 1

#    def parseDoc( self, response ):
        
