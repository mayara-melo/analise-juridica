# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
import html2text
from stf.items import StfItem
import re

def findId( text):
    return text


class STFSpider(BaseSpider):

    name = 'stfSpider'

    def __init__ ( self, iDate, fDate, page, index):
        self.domain = 'stf.jus.br'
        self.ids = {}
        self.relators = {}
        self.ufs = {}
        self.dataJulgs = {}
        self.tags = {}
        self.partesType = {}
        self.index = int(index)
        self.fIndex = int(index)
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
        text = html2text.html2text( text)
        text = text.encode('utf-8')
        text = text.replace('\n\n', '')
        text = text.replace('\r\n', '')
        return text

    def orderSections( self, sectHeaders, sectBody, possHeaders):
        sections = {}
        for i,ph in enumerate(possHeaders):
            for j, sh in enumerate(sectHeaders):
                sh = self.parseItem( sh)
                if (sh.startswith( ph)):
                    sections[i] = sectBody[j]
                    break
        return sections

    def getAcordaosQuotes( self, txt):
        quotes = []
        data = re.search("Ac.rd.o[s]? citado[s]?\s*:\s*([^\.]*)", txt)
        if data:
            data = (data.group(1)).replace(',',' ')
            data = data.split(' ')
            for q in data:
                q = q.replace('(', '')
                q = q.replace(')', '')
                q = q.replace('\r','')
                q = q.replace('\n','')
                q = q.replace(' ', '')
                q = q.replace('-', ' ')
                if q: 
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
        i=0
        for doc in body:
            print 'index: '+str( i)
            title = doc.xpath('p[1]/strong/text()').extract()
            titleLine = re.match('\s*([\w -]+)\/\s([A-Za-z]{2}).*', title[0])
            acordaoId = self.parseItem( (titleLine.group(1)).replace('-',' '))
            uf = self.parseItem( titleLine.group(2))
            relator = self.parseItem(re.match('\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)', title[7] ).group(1))
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
            self.fIndex += 1
            sections = self.orderSections(  sectHeaders, sectBody, possHeaders)
            decision = tags = laws = obs = doutrines = quotes = result =''
            keys = sections.keys()
            if 0 in keys:
                decision = self.parseItem(sections[0].extract())
            if 1 in keys:
                tags = self.parseItem(sections[1].extract())
            if 2 in keys:
                laws = self.parseItem(sections[2].extract())
            if 3 in keys:
                obs = self.parseItem(sections[3].extract())
                quotes = self.getAcordaosQuotes( obs)
            if 4 in keys:
                doutrines = self.parseItem(sections[4].extract())
            i = i + 1
            yield StfItem(
                acordaoId   = acordaoId,
                uf          = uf,
#                publicacao  = publicacao,
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
                filename    = 'stf'+str(self.fIndex).zfill(6)+'.xml'
            ) 
#            self.printItem(item)
   #         self.testItem(item)
        #    self.printItem(item)
           # f = open( '../files/stf'+str(self.index).zfill(6)+'.xml', 'w' )
           # f.write(html2text.html2text( div ).encode('utf-8'))
           # self.index = self.index + 1
#        self.writeTestLog( self.relators, 'tests/relatorsList')
 #       self.writeTestLog( self.ids, 'tests/idsList')
  #      self.writeTestLog( self.ufs, 'tests/ufsList')
   
    def addToDict( self, dic, item):
        keys = dic.keys()
        if item in keys:
            dic[item] += 1
        else:
            dic[item] = 1
        return dic

    def testItem( self, item):
        self.relators = self.addToDict( self.relators, item['relator'])
        self.ids = self.addToDict( self.ids, item['acordaoId'])
        self.ufs = self.addToDict( self.ufs, item['uf'])
    
    def writeTestLog(self, dataDict, outputFile):
        with open( outputFile, 'a') as f:
            for v in dataDict.keys():
                data = v.encode('utf-8').strip()+' :'+ '{:<30}'.format(str( dataDict[v]))
                f.write( data) 
                f.write('\n-------------------------------------------------------------\n')
     
    def printItem( self, item):
        print '-------------------------------------------------------------'
        print 'relator:\n'+item['relator']
        print '\nId:\n'+item['acordaoId']
        print '\nuf:\n'+item['uf']
        print '\ndataJulg:\n'+item['dataJulg']
#        print '\norgaoJulg:\n'+item['orgaoJulg']
#        print '\npublic:\n'+item.publicacao
        print '\npartes:\n'+item['partes']
        print '\nementa:\n'+item['ementa']
        print '\ndecisao:\n'+item['decisao']
        print '\nindexacao:\n'+item['tags']
        print '\nleis:\n'+item['legislacao']
        print '\ndoutrinas:\n'+item['doutrinas']
        print '\nobs:\n'+item['observacao']
#        print '\nresult:\n'+result
        print '\n\nquotes:\n'
        print item['citacoes']
        print '-------------------------------------------------------------'
 
        
         
