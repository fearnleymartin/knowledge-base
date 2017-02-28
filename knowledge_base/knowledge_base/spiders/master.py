# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from cssselect import GenericTranslator
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import time
import re


class MasterSpider(CrawlSpider):
    name = "master"
    allowed_domains = []

    gt = GenericTranslator()
    rate_limit = False

    def __init__(self):
        super().__init__()
        if self.rate_limit:
            self.new_search_page_pause_time = 0.8
            self.captcha_pause_time = 20
        else:
            self.new_search_page_pause_time = 0
            self.captcha_pause_time = 0
        self.search_page_count = 0
        self.captcha_count = 0
        self.start_time = time.time()
        self.total_items = 0

    def parse_start_url(self, response):
        """For parsing the starting page"""
        return self.identify_and_parse_page(response)

    def identify_and_parse_page(self, response):
        """
        :param response:
        :return:
        """

        # check whether search page or question page
        if self.is_index_page(response.url):  # if search page, extract link and next page
            self.process_index_page(response)
        elif self.is_captcha_page(response.url):
            self.process_captcha(response)
        else:  # if question page, parse post
            question_answer = self.parse_items(response)
            if question_answer:
                yield question_answer

    def is_index_page(self, url):
        """
        @TODO: generalise
        :param url:
        :return: True if url is a page that list search results
        """
        pass

    def is_captcha_page(self, url):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        pass

    def process_index_page(self, response):
        """
        At the moment just logs that we have an index page, and pauses
        :return:
        """
        logging.info('new search page')
        logging.info(response.url)
        self.search_page_count += 1
        print('new search page')
        print('pausing')
        time.sleep(self.new_search_page_pause_time)
        print('restarting')

    def process_captcha(self, response):
        """

        :param response:
        :return:
        """
        logging.info('captcha problem')
        self.captcha_count += 1
        print('captcha detected')
        print('pausing')
        time.sleep(self.captcha_pause_time)
        print('restarting')

    def parse_date(self, date_string):
        """
        Return standardised date strings. The idea is to have a list of different possible formats and try them all out
        :param date_string:
        :return:
        """
        date_formats = ['%b %d, %Y at %I:%M %p', '%b %d at %H:%M']
        date_string = re.sub('^0|(?<= )0', '', date_string)
        for date_format in date_formats:
            try:
                res = str(datetime.strptime(date_string, date_format))
                return res
            except ValueError:
                pass
        return None

    def parse_items(self, response):
        pass