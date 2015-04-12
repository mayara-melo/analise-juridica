# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

#from scrapy.stf import settings
from scrapy.exceptions import DropItem
from scrapy import log
from scrapy.contrib.exporter import XmlItemExporter

class MongoDBPipeline(object):

    def __init__(self):
        a = 1
        connection = pymongo.Connection(
            'localhost',
            27017
        )
        db = connection['DJs']
        self.collection = db['stj']

    def process_item(self, item, spider):
        valid = True
#        print 'processing item'
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.insert(dict(item))
            log.msg("item added!",
                    level=log.DEBUG, spider=spider)
        return item

#class StjPipeline(object):
#
#    def __init__(self):
#        self.files = {}
#
#    def process_item(self, item, spider):
#            file = open( '../files/'+item['filename']+'.xml', 'w+b')
#        self.exporter = XmlItemExporter(file)
#        self.exporter.start_exporting()
#        self.exporter.export_item(item)
#        self.exporter.finish_exporting()
#        file.close()
#
