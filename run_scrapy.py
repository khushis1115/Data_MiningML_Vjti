from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import sys
sys.path.append('C:/Users/amits/PycharmProjects/vjti2024')

from one import OneSpider  # Adjust the import based on your project structure

process = CrawlerProcess({
    'FEED_FORMAT': 'json',
    'FEED_URI': 'output.json'
})

process.crawl(OneSpider)
process.start()
