# Scrapy settings for stf project
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
	'stj.pipelines.StjPipeline':1,
}
SPIDER_MODULES = ['stj.spiders']
NEWSPIDER_MODULE = 'stj.spiders_dev'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stf (+http://www.yourdomain.com)'
