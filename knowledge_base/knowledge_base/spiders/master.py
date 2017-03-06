# -*- coding: utf-8 -*-

from cssselect import GenericTranslator
from scrapy.spiders import CrawlSpider
from datetime import datetime
import logging
import time
import re
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from ..items import QuestionAnswer


class MasterSpider(CrawlSpider):
    """
    Base class spider from which other spiders inherit
    Gives the basic functions and layout of spider
    (Not meant to be run, but should be subclassed (for the moment))
    The idea is to put all the crawler logic in here, and let the subclasses implement site specific scraping
    Follows the index crawler pattern: i.e. start url is a paginated index of links (e.g. search results).
    Will crawl the given links and iterate through the index pagination
    """
    name = "master"
    allowed_domains = ['superuser.com']
    custom_settings = {'DOWNLOAD_DELAY': 0.45,
                       'LOG_FILE': 'logs/master_log.txt'
                       }

    gt = GenericTranslator()  # For converting css classes to xpaths
    rate_limit = False   # for imposing download rate limit (to avoid captchas)

    product = 'outlook'

    start_urls = ['http://superuser.com/search?q={}'.format(product)]

    # These allows define the crawling
    allow = ()
    deny = ()
    restrict_xpaths = ()
    rules = (
        # @TODO implement
        Rule(LinkExtractor(allow=allow,  # Allow index and results pages
                           deny=deny,  # Other pages
                           restrict_xpaths=restrict_xpaths),  # Pagination, results pages
             callback="identify_and_parse_page",
             process_links="process_links",
             follow=True),
    )

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
        print(response.url)
        # check whether search page or question page
        if self.is_index_page(response.url):  # if search page, extract link and next page
            self.process_index_page(response)
        elif self.is_captcha_page(response.url):
            self.process_captcha(response)
        elif self.is_results_page(response):
            items = self.process_question_answer_page(response)
            return items
        else:  # if question page, parse post
            print('other')

    ### Page processing functions

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
        # TODO: implement going through pagination of forums responses
        # All posts on page (might be posts on other pages though, )
        print('results page')

        # Filters
        if not self.is_page_relevant(response):  # check we are talking about the right thing
            return None
        if not self.page_contains_answers(response):
            return None

        # process posts
        posts = []
        question_answer_list = []
        for post_number, post in enumerate(posts):
            question_answer = QuestionAnswer()
            question_answer = self.fill_question(response, question_answer)
            question_answer = self.fill_answer(response, question_answer, post_number)
            question_answer_list.append(question_answer)

        return question_answer_list

    ### Q/A parsing functions

    def fill_question(self, response, question_answer):
        """
        Called by process_question_answer_page
        :param response:
        :param question_answer:
        :return: question_answer item object with question attributes filled in
        """
        return question_answer

    def fill_answer(self, response, question_answer, answer_number):
        """
        Called by process_question_answer_page
        :param response:
        :param question_answer:
        :param answer_number: position of answer/reply on page
        :return: question_answer item object with answer attributes filled in corresponding to the answer number
        """
        return question_answer


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

    ### Filter functions

    def filter_posts(self, response, posts):
        """
        :param response:
        :return: Valid Q/A pairs from all posts
        """
        return posts

    def is_page_relevant(self, response):
        """

        :return: true if page related to topic
        """
        if self.product in response.text:
            return True
        else:
            return False

    def page_contains_answers(self, response):
        """
        Checks that results page has at least one answer
        :param response:
        :return:
        """
        pass

    ### Page identification functions

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

    def is_results_page(self, url):
        """
        A results page is a page contain Q/A pairs
        :param url:
        :return: true if is a results page
        """
        # @TODO decide on the type this function takes
        return True

    def process_links(self, links):
        """
        Processes and filters links obtained by the link extractor
        :param links:
        :return:
        """
        filtered_links = []
        for link in links:
            if self.is_index_page(link.url):
                filtered_links.append(link)
            elif self.is_results_page(link.url):
                filtered_links.append(link)
            else:
                pass
        return filtered_links
