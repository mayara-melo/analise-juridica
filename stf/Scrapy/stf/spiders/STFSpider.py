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
            '%29'+
            '&pagina='+page+
            '&base=baseAcordaos'
        ]
    
    def parseItem( self, item ):
       # text = item.replace("&nbsp", '')
       # text = html2text.html2text( text)
        text = item.encode('utf-8')
       # text = text.replace('\n\n', '')
       # text = text.replace('\r\n', '')
        return text

    def orderSections( self, sectHeaders, sectBody, possHeaders):
        sections = {}
        for i,ph in enumerate(possHeaders):
            for j, sh in enumerate(sectHeaders):
                if (sh.startswith( ph)):
                    sections[i] = sectBody[j].encode('utf-8')
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
            title = doc.xpath('p[1]/strong/text()').extract()
            titleLine = re.match('\s*([\w -]+)\/\s*(\w*)\s*-\s*(.*).*', title[0].encode('utf-8'))
            #acordaoId = self.parseItem( (titleLine.group(1)).replace('-',' '))
            acordaoId = titleLine.group(1).replace('-',' ')
#            uf = self.parseItem( titleLine.group(2))
            ufShort = titleLine.group(2)
            uf = titleLine.group(3)
            relator = re.match('\s*Relator\(a\):.+[Mm][Ii][Nn].\s*(.+)', title[7] ).group(1)
            dataJulg = orgaoJulg =''
            for line in title[1:]:
                line = line.encode('utf-8')
                line = line.replace('&nbsp', '')
                if line.startswith('Julgamento'):
                    julgLine = re.match('Julgamento:\s*([\d\/]+)\s*.* Julgador:\s*(.*)', line)
                    dataJulg = julgLine.group(1)
                    orgaoJulg = julgLine.group(2)
                    break
            publicacao = doc.xpath('pre[1]/text()').extract()[0]            
            ementa = doc.xpath('strong[1]/p/text()').extract()[1]
            sectHeaders = doc.xpath('p/strong/text()').extract()[len(title)+1:-1]
            sectBody = doc.xpath('pre/text()').extract()[1:]
            possHeaders = [
                'Parte',   
                'Decis',     # strong/p/strong/text() sec strong/p
                'Indexa',   # p/strong/text() sec next pre
                'Legisla',  # p/strong/text() sec next pre
                'Observa',  # p/strong/text() sec next pre
                'Doutrina'    # p/strong/text() sec next pre
            ]
            self.fIndex += 1
            sections = self.orderSections(  sectHeaders, sectBody, possHeaders)
            decision = tags = laws = obs = doutrines = quotes = result =''
            
            partes = self.getFoundSection( 0, sections)
            decision = self.getFoundSection( 1, sections)
            tags = self.getFoundSection( 2, sections)
            laws = self.getFoundSection( 3, sections)
            obs = self.getFoundSection( 4, sections)
            doutrines = self.getFoundSection( 5, sections)
            if tags:
                tags = re.split(r'[\n,\-.]+', tags)
                for j in range( len(tags)):
                    tags[j] = tags[j].strip()
                tags = filter(None, tags)
            if obs:
                quotes = self.getAcordaosQuotes( obs)
            yield StfItem(
                acordaoId   = acordaoId,
                localSigla  = ufShort,
                local       = uf,
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
        print '\nindexacao:\n'
        print item['tags']
        print '\nleis:\n'+item['legislacao']
        print '\ndoutrinas:\n'+item['doutrinas']
        print '\nobs:\n'+item['observacao']
#        print '\nresult:\n'+result
        print '\n\nquotes:\n'
        print item['citacoes']
        print '-------------------------------------------------------------'
 
        
         
