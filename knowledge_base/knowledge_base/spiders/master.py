# -*- coding: utf-8 -*-

from cssselect import GenericTranslator
from scrapy.spiders import CrawlSpider
import logging
import time
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from ..items import QuestionAnswer
from ..scripts.is_index_page import IsIndexPage
from ..scripts.is_results_page import IsResultsPage
from scrapy_splash import SplashRequest


class MasterSpider(CrawlSpider):
    """
    Base class spider from which other spiders inherit
    Gives the basic functions and layout of spider
    This class should be subclasses
    The idea is to put the general crawler logic in here, and let the subclasses implement site specific scraping
    """

    # Parameters
    product = None
    start_urls = ["https://forum.eset.com/forum/49-general-discussion/"]
    rate_limit = False  # for imposing download rate limit (to avoid captchas)

    # class initialisation
    name = "master"
    gt = GenericTranslator()  # For converting css classes to xpaths
    logger = logging.getLogger('datefinder')
    logger.setLevel(logging.INFO)

    # Parameters for url-guiding method
    allow = ()
    deny = ('login', 'password', 'misc', 'members', 'register', 'contact',)
    restrict_xpaths = ()

    # Examples:

    # community dynamics
    # allow += ('/t/', '/p/', '/f/')
    # deny += ('/tags/',)
    # restrict_xpaths += (gt.css_to_xpath('.post-name'), gt.css_to_xpath('.pager'))

    # mac rumors
    # allow += ('threads', 'forum')
    # deny += ('members',)
    # restrict_xpaths += (gt.css_to_xpath('.listBlock'),
    #                    gt.css_to_xpath('.PageNav'))

    # reddit
    # allow += ('/r/iphonehelp/',)
    # deny += ('/user/', "/login", )
    # restrict_xpaths += (gt.css_to_xpath('.entry'),
    #                    gt.css_to_xpath('.nav-buttons'))

    # spiceworks
    # allow += ('/topic/', '/windows')
    # deny += ('/people/', "/pages", 'service-providers', )
    # restrict_xpaths += (gt.css_to_xpath('.topics'),
    #                    gt.css_to_xpath('.sui-pagination'))

    # eset
    # allow += ('/topic/', '/forum')
    # deny += ('/login', "/profile",)
    # restrict_xpaths += (gt.css_to_xpath('.ipsDataItem_main'),
    #                    gt.css_to_xpath('.ipsPagination'))

    # allow = ('threads', 'forum')
    # deny = ('members')
    # restrict_xpaths = (gt.css_to_xpath('.listBlock'),
    #                    gt.css_to_xpath('.PageNav'))

    # allow = ()
    # deny = ()
    # restrict_xpaths = ()

    rules = (
        Rule(LinkExtractor(allow=allow,  # Allow index and results pages
                           deny=deny,  # Deny other pages
                           restrict_xpaths=restrict_xpaths),  # Pagination, results pages
             callback="identify_and_parse_page",
             process_links="process_links",
             follow=True),
    )

    def __init__(self):
        super().__init__()
        if self.rate_limit:
            self.new_index_page_pause_time = 0.8
            self.captcha_pause_time = 20
        else:
            self.new_index_page_pause_time = 0
            self.captcha_pause_time = 0

        # Initialise basic crawl starts
        self.index_page_count = 0
        self.results_page_count = 0
        self.captcha_count = 0
        self.start_time = time.time()
        self.total_items = 0
        self.isResultsPage = IsResultsPage(product=self.product)
        self.isIndexPage = IsIndexPage(product=self.product)

    def parse_start_url(self, response):
        """For parsing the starting page"""
        yield SplashRequest(url=response.url, callback=self.identify_and_parse_page, args={'wait':0.5})

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding parsing procedure
        :param response:
        :return:
        """
        # print("processing: {}".format(response.url))
        if self.initial_page_filter(response):
            if self.is_index_page(url=response.url, response=response):
                self.process_index_page(response)
            elif self.is_captcha_page(response.url, response):
                self.process_captcha(response)
            elif self.is_results_page(response.url, response):
                items = self.process_question_answer_page(response)
                return items
            else:
                self.classification_file.write("other, {}\n".format(response.url))
                print('other: {}'.format(response.url))
        else:
            self.classification_file.write("other, {}\n".format(response.url))
            print('other: {}'.format(response.url))

    ### Page processing functions

    def process_index_page(self, response):
        """
        At the moment just logs that we have an index page, and pauses
        :return:
        """
        logging.info('index: {}'.format(response.url))
        print('index: {}'.format(response.url))
        self.classification_file.write("index, {}\n".format(response.url))
        self.index_page_count += 1
        time.sleep(self.new_index_page_pause_time)

    def process_captcha(self, response):
        """
        If a captcha page is detected, we pause the crawler
        N.B. Should be needed with autothrottling
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
        For extracting information from question/answer pages or forum threads
        Called by identify_and_parse_page
        :param response:
        :return:
        """
        self.results_page_count += 1
        self.classification_file.write("results, {}\n".format(response.url))
        logging.info('results: {}'.format(response.url))
        print("results: {}".format(response.url))

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

    def initial_page_filter(self, response):
        """ To quickly filter out unsuitable pages without running entire algorithm"""
        # match = re.match('<xml', response.body)
        # if match:
        #     return False
        # else:
        #     return True
        return True

    ### Page identification functions

    def is_index_page(self, url, response=None):
        """
        :param url:
        :return: True if page is an index of links (e.g. search results), False otherwise
        """
        return self.isIndexPage.is_index_page(url, response)

    def is_captcha_page(self, url, response=None):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return 'captcha' in url

    def is_results_page(self, url, response=None):
        """
        A results page is a page that contains Q/A pairs
        :param url:
        :param response:
        :return: true if is a results page
        """
        return self.isResultsPage.is_results_page(url, response)


