# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import logging
import time


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        logging.info('captcha count: {}'.format(spider.captcha_count))
        logging.info('total search page count: {}'.format(spider.search_page_count))
        total_time = time.time() - spider.start_time
        logging.info('total time: {}'.format(total_time))
        logging.info('total items: {}'.format(spider.total_items))
        try:
            logging.info('crawl speed: {}'.format(spider.total_items/total_time))
        except ZeroDivisionError:
            pass
        self.file.close()

    def process_item(self, item, spider):
        spider.total_items += 1
        question_answer_pair = {'question': {k: v for (k, v) in dict(item).items() if k[0] == 'q'},
                                'answer': {k: v for (k, v) in dict(item).items() if k[0] == 'a'}}

        line = json.dumps(question_answer_pair)
        # print('line', line)
        self.file.write(line + '\n')
        return item
