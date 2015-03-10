# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
import html2text
from stf.items import StfItem


class STFSpider(BaseSpider):

    name = 'stf'

    def __init__ ( self, iDate, fDate, page, index):
        self.domain = 'stf.jus.br'
        self.index = int(index)
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

    def parse( self, response ):
        print "\n\n\n\n"
        sel = Selector(response)
        body = sel.xpath(
            '/html/body/div[@id="pagina"]'+
            '/div[@id="conteiner"]'+
            '/div[@id="corpo"]'+
            '/div[@class="conteudo"]'+
            '/div[@id="divImpressao"]'+
            '/div[@class="abasAcompanhamento"]'
        )
        for tag in body:
            div = tag.xpath('div[@class="processosJurisprudenciaAcordaos"]').extract()[0]
            f = open( '../files/stf'+str(self.index).zfill(6)+'.xml', 'w' )
            f.write(html2text.html2text( div ).encode('utf-8'))
            self.index = self.index + 1
