# -*- coding: utf-8 -*-

from cssselect import GenericTranslator
from scrapy.spiders import CrawlSpider
from datetime import datetime
import logging
import time
import re


class MasterSpider(CrawlSpider):
    """
    Base class spider from which other spiders inherit
    Gives the basic functions and layout of spider
    Not meant to be run, but should be subclassed
    Follows the index crawler pattern: i.e. start url is a paginated index of links (e.g. search results).
    Will crawl the given links and iterate through the index pagination
    """
    name = "master"
    allowed_domains = []

    gt = GenericTranslator()  # For converting css classes to xpaths
    rate_limit = False   # for imposing download rate limit (to avoid captchas)

    def __init__(self):
        super().__init__()
        if self.rate_limit:
            self.new_search_page_pause_time = 0.8
            self.captcha_pause_time = 20
        else:
            self.new_search_page_pause_time = 0
            self.captcha_pause_time = 0
        # Initialise basic crawl starts
        self.search_page_count = 0
        self.captcha_count = 0
        self.start_time = time.time()
        self.total_items = 0

    def parse_start_url(self, response):
        """For parsing the starting page"""
        return self.identify_and_parse_page(response)

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding procedure
        :param response:
        :return:
        """

        # check whether search page or question page
        if self.is_index_page(response.url):  # if search page, extract link and next page
            self.process_index_page(response)
        elif self.is_captcha_page(response.url):
            self.process_captcha(response)
        else:  # if question page, parse post
            items = self.process_question_answer_page(response)
            return items

    def is_index_page(self, url):
        """
        :param url:
        :return: True if page is an index of links (e.g. search results), False otherwise
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

    def process_question_answer_page(self, response):
        """
        To override
        For extracting information from question/answer pages or forum threads
        Called by identify and parse page
        :param response:
        :return:
        """

    def fill_question(self, response, question_answer):
        """
        Called by process_question_answer_page
        :param response:
        :param question_answer:
        :return: question_answer item object with question attributes filled in
        """

    def fill_answer(self, response, question_answer, answer_number):
        """
        Called by process_question_answer_page
        :param response:
        :param question_answer:
        :param answer_number: position of answer/reply on page
        :return: question_answer item object with answer attributes filled in corresponding to the answer number
        """



    ### HELPER FUNCTIONS

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