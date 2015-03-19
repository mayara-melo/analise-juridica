# Scrapy settings for stf project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'stf'

ITEM_PIPELINES = {
    'stf.pipelines.MongoDBPipeline':1,
}

SPIDER_MODULES = ['stf.spiders']
NEWSPIDER_MODULE = 'stf.spiders_dev'

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "test"
MONGODB_COLLECTION = "stf"
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stf (+http://www.yourdomain.com)'
