# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import logging
import time
from datetime import datetime
from urllib.parse import urlparse
from .utils import date_to_solr_format, url_to_short_file_name
import uuid


class GeneralPipeline(object):
    """
    Base pipeline from which others inherit
    Opens items csv
    Logs crawl stats on spider close
    """
    def open_spider(self, spider):
        # TODO: regexify
        url_path = url_to_short_file_name(spider.start_urls[0])
        items_file_path = 'scraped_data/{}_items.jl'.format(url_path)
        # items_file_path = 'scraped_data/multi_site_items.jl'
        print('items file path', items_file_path)
        self.file = open(items_file_path, 'w')

    def close_spider(self, spider):
        logging.info('captcha count: {}'.format(spider.captcha_count))
        logging.info('index page count: {}'.format(spider.index_page_count))
        logging.info('results page count: {}'.format(spider.results_page_count))
        total_time = time.time() - spider.start_time
        logging.info('total time: {}'.format(total_time))
        logging.info('total items: {}'.format(spider.total_items))
        try:
            logging.info('crawl speed: {}'.format(spider.total_items/total_time))
        except ZeroDivisionError:
            pass
        self.file.close()
        try:
            logging.info('duplicate count: {}'.format(spider.duplicate_count))
        except:
            pass
        spider.classification_file.close()


class JsonWriterPipeline(GeneralPipeline):
    """
    Processes items (Q/A pairs) and writes them to json
    """

    def process_item(self, item, spider):
        spider.total_items += 1
        question_answer_pair = {
            'uid': str(uuid.uuid1()),
            'product': spider.product,
            'source_url': item['source_url'],
            'source_domain': urlparse(item['source_url']).netloc,
            'crawl_date': date_to_solr_format(datetime.now()),
            'question': {k: v for (k, v) in dict(item).items() if k[0] == 'q'},
            'answer': {k: v for (k, v) in dict(item).items() if k[0] == 'a'}
        }

        line = json.dumps(question_answer_pair)
        self.file.write(line + '\n')
        return item


class IsSiteValidPipeline(GeneralPipeline):
    """
    Prints some extra stats on crawl close
    """
    def close_spider(self, spider):
        logging.info('captcha count: {}'.format(spider.captcha_count))
        logging.info('index page count: {}'.format(spider.index_page_count))
        logging.info('results page count: {}'.format(spider.results_page_count))
        total_time = time.time() - spider.start_time
        logging.info('total time: {}'.format(total_time))
        logging.info('total items: {}'.format(spider.total_items))
        try:
            logging.info('crawl speed: {}'.format(spider.total_items/total_time))
        except ZeroDivisionError:
            pass
        logging.info('results pages: {}'.format(spider.results_pages))
        logging.info('index pages: {}'.format(spider.index_pages))
        logging.info('other pages: {}'.format(spider.other_pages))
        self.file.close()
        spider.classification_file.close()

