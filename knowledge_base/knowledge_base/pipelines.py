# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        question_answer_pair = {'question': {k: v for (k, v) in dict(item).items() if k[0] == 'q'},
                                'answer': {k: v for (k, v) in dict(item).items() if k[0] == 'a'}}

        line = json.dumps(question_answer_pair)
        # print('line', line)
        self.file.write(line)
        return item
