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
from ..scripts.is_index_page import IsIndexPage
from ..scripts.is_results_page import IsResultsPage
from ..utils import url_to_short_file_name
import scrapy
from scrapy_splash import SplashRequest


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
    allowed_domains = ['superuser.com', 'macrumors.com', 'answers.microsoft.com',
                       'tomsguide.com', 'cnet.com']
    custom_settings = {'DOWNLOAD_DELAY': 0.45,
                       'LOG_FILE': 'logs/master_simple_log.txt'
                       }

    gt = GenericTranslator()  # For converting css classes to xpaths
    rate_limit = False   # for imposing download rate limit (to avoid captchas)

    product = 'outlook'
    logger = logging.getLogger('datefinder')
    logger.setLevel(logging.INFO)
    start_urls = ['https://www.cnet.com/']

    # classification_file_path = 'scraped_data/classification/{}_classification_file.csv'.format(url_to_short_file_name(start_urls[0]))
    # print(classification_file_path)
    # classification_file = open(classification_file_path, 'w')

    # start_urls = ['http://superuser.com/search?q={}'.format(product)]
    # start_urls = ['https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/']
    # start_urls = ['https://answers.microsoft.com/en-us/search/search?SearchTerm=powerpoint&IsSuggestedTerm=false&tab=&CurrentScope.ForumName=msoffice&CurrentScope.Filter=msoffice_powerpoint-mso_win10-mso_o365b&ContentTypeScope=&auth=1#/msoffice/msoffice_powerpoint-mso_win10-mso_o365b//1']

    # These allows define the crawling
    # allow = ()
    # deny = ('login', 'password', 'misc', 'members', 'register', 'contact',)
    # restrict_xpaths = ()

    allow = ('/t/', '/p/', '/f/')

    deny = ('/tags/')
    restrict_xpaths = (gt.css_to_xpath('.post-name'), gt.css_to_xpath('.pager'))

    # allow = ('threads', 'forum')
    # deny = ('members')
    # restrict_xpaths = (gt.css_to_xpath('.listBlock'),
    #                    gt.css_to_xpath('.PageNav'))


    rules = (
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
        # meta = {'splash': {'args': {'html': 1}}}
        # yield scrapy.Request(url=response.url, callback=self.identify_and_parse_page, meta=meta)
        yield SplashRequest(url=response.url, callback=self.identify_and_parse_page, args={'wait':0.5})


        # return self.identify_and_parse_page(response)

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
        self.results_page_count += 1
        self.classification_file.write("results, {}\n".format(response.url))
        logging.info('results: {}'.format(response.url))
        print("results: {}".format(response.url))


        # TODO: implement going through pagination of forums responses
        # All posts on page (might be posts on other pages though, )
        # print('results page')

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

    def initial_page_filter(self, response):
        """ To quickly filter out unsuitable pages"""
        # TODO implement
        return True
        match = re.match('<xml', response.body)
        if match:
            return False
        else:
            return True

    ### Page identification functions

    def is_index_page(self, url, response=None):
        """
        :param url:
        :return: True if page is an index of links (e.g. search results), False otherwise
        """
        # TODO get clues from response and not just from url
        # if response is None:
        #     index_clues = ['/search', '/forums/']
        #     for index_clue in index_clues:
        #         if index_clue in url:
        #             return True
        #     return False
        # else:
            # print('response in master is not none for url{} : {}'.format(url, response is not None))
        # index_clues = ['/search', '/forums/']
        # for index_clue in index_clues:
        #     if index_clue in url:
        #         return True
        return self.isIndexPage.is_index_page(url, response)


    def is_captcha_page(self, url, response=None):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        # TODO get clues from response and not just from url
        'captcha' in url

    def is_results_page(self, url, response=None):
        """
        A results page is a page that contains Q/A pairs
        :param url:
        :return: true if is a results page
        """
        # TODO get clues from response and not just from url
        # if response is None:
        #     result_clues = ['/questions', '/threads', '/forum']
        #     for result_clue in result_clues:
        #         if result_clue in url:
        #             return True
        #     return False
        # else:
        # result_clues = ['/questions', '/threads', '/forum']
        # for result_clue in result_clues:
        #     if result_clue in url:
        #         return True
        return self.isResultsPage.is_results_page(url, response)
        # return True

    def process_links(self, links):
        """
        Processes and filters links obtained by the link extractor
        :param links:
        :return:
        """
        filtered_links = []
        for link in links:
            # if self.is_index_page(link.url):
            #     filtered_links.append(link)
            # elif self.is_results_page(link.url):
            #     filtered_links.append(link)
            # else:
            #     pass
            filtered_links.append(link)
        return filtered_links

    ### Pre treatment functions


