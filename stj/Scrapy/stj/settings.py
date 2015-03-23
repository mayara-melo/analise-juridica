# Scrapy settings for stj project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'stj'
FEED_EXPORTERS_BASE = {
    'xml': 'scrapy.contrib.exporter.XmlItemExporter',
}
ITEM_PIPELINES = {
	'stj.pipelines.MongoDBPipeline':1,
}
SPIDER_MODULES = ['stj.spiders']
NEWSPIDER_MODULE = 'stj.spiders_dev'

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "test"
MONGODB_COLLECTION = "stj"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stf (+http://www.yourdomain.com)'
