# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

#from scrapy.stf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from stf.items import StfItem
from CorpusBuilder import CorpusBuilder


class MongoDBPipeline( object):

    def __init__( self):
        connection = pymongo.Connection(
            'localhost',
            27017
        )
        db = connection['DJs']
        self.collection = db['stf']
        self.corpus = None

    def process_item( self, item, spider):
        valid = True
#        print 'processing item'
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.insert(dict(item))
            log.msg("Question added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
            self.addItemToCorpus( item, self.corpus)
        return item

    def open_spider( self, spider):
        self.corpus = CorpusBuilder()

    def close_spider( self, spider):
        self.corpus.print2File( "corpusSTF")

    def addItemToCorpus( self, item, corpus):
        corpus.addWords( item['local'])
        corpus.addWords( item['partes'])
        corpus.addWords( item['ementa'])
        corpus.addWords( item['decisao'])
        corpus.addWords( item['observacao'])
        for w in item["tags"]:
            corpus.addWords( w)

