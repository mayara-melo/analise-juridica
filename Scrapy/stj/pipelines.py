# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.contrib.exporter import XmlItemExporter


class StjPipeline(object):

    def __init__(self):
        self.files = {}

    def process_item(self, item, spider):
        file = open( '../files/'+item['filename']+'.xml', 'w+b')
        self.exporter = XmlItemExporter(file)
        self.exporter.start_exporting()
        self.exporter.export_item(item)
        self.exporter.finish_exporting()
        file.close()

