# -*- coding: utf-8 -*-

from .master import MasterSpider
from scrapy.extensions.closespider import CloseSpider
import logging
import time


def page_count_with_log(self, response, request, spider):
    self.counter['pagecount'] += 1
    if self.counter['pagecount'] == self.close_on['pagecount']:
        logging.info('site not valid')
        self.crawler.engine.close_spider(spider, 'closespider_pagecount')


class IsSiteValidSpider(MasterSpider):
    """
    The aim if this crawler is to detect whether a website contains both index and results pages.
    In this case we say that the site is valid
    """
    name = "isSiteValid"
    allowed_domains = ["macrumors.com"]
    start_urls = ['http://www.macrumors.com']

    CloseSpider.page_count = page_count_with_log

    def __init__(self):
        self.rate_limit = False
        super().__init__()
        self.contains_index_page = False
        self.contains_results_page = False
        self.index_pages = []
        self.results_pages = []
        self.other_pages = []

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding parsing procedure
        :param response:
        :return:
        """
        if self.contains_index_page and self.contains_results_page:
            print('should stop now')
            self.crawler.engine.close_spider(self, 'site is valid')
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

    ### Filter functions

    def is_page_relevant(self, response):
        """
        Check product is in tags
        :param response:
        :return:
        """
        return True

    def page_contains_answers(self, response):
        """

        :param response:
        :return: true if page has more than one post
        """
        return True

    def filter_posts(self, response, posts):
        """
        TODO: implement
        Return only pertinant Q/A pairs
        :param response:
        :param posts:
        :return:
        """
        return posts




