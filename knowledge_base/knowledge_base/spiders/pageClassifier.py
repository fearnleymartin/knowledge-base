# -*- coding: utf-8 -*-

# from ..items import QuestionAnswer
# from datetime import datetime
# from bs4 import BeautifulSoup
# import re
from .master import MasterSpider
# from ..utils import date_to_solr_format
from scrapy.extensions.closespider import CloseSpider
import logging
import time


class PageClassifier(MasterSpider):
    """
    """
    name = "pageClassifier"
    allowed_domains = ["macrumors.com"]


    start_urls = ['http://www.macrumors.com']


    def __init__(self):
        self.rate_limit = False
        super().__init__()
        self.contains_index_page = False
        self.contains_results_page = False
        self.index_pages = []
        self.results_pages = []
        self.other_pages = []

    custom_settings = {
        'LOG_FILE': 'logs/simple_log.txt',
        'CLOSESPIDER_PAGECOUNT': 2,
        'ITEM_PIPELINES': {
            'knowledge_base.pipelines.IsSiteValidPipeline': 300,
        }

    }

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding parsing procedure
        :param response:
        :return:
        """

        # print("call back response is not none: {}".format(response is not None))
        # print("processing: {}".format(response.url))
        if self.is_index_page(url=response.url, response=response):
            self.process_index_page(response)
        elif self.is_captcha_page(response.url, response):
            self.process_captcha(response)
        elif self.is_results_page(response.url, response):
            self.process_question_answer_page(response)
        else:
            self.classification_file.write("other, {}\n".format(response.url))
            self.other_pages.append(response.url)
            print('other: {}'.format(response.url))

    def process_question_answer_page(self, response):
        """
        :param response:
        :return:
        """

        self.contains_results_page = True
        self.results_page_count += 1
        self.results_pages.append(response.url)
        self.classification_file.write("results, {}\n".format(response.url))
        logging.info('results: {}'.format(response.url))
        print("results: {}".format(response.url))

    def process_index_page(self, response):
        """

        :param response:
        :return:
        """
        self.contains_index_page = True
        self.index_pages.append(response.url)
        logging.info('index: {}'.format(response.url))
        print('index: {}'.format(response.url))
        self.classification_file.write("index, {}\n".format(response.url))

        self.index_page_count += 1
        time.sleep(self.new_index_page_pause_time)






