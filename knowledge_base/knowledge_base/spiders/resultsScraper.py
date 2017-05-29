# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from .master import MasterSpider
from ..utils import date_to_solr_format, url_to_short_file_name
import logging
from scrapy_splash import SplashRequest
from urllib.parse import urlparse
import time


class resultsScraper(MasterSpider):
    """
    This spider will crawl any web page and extract Q/A pairs to a jsonlines file
    It works by classifying the pages as results pages or other and parsing results pages with an algorithm using the html structure of the page
    You must specify the start_url and you can optionally specify the product
    """

    # Parameters to set
    product = None
    start_urls = ["https://forum.eset.com/forum/49-general-discussion/"]

    # class initialisation
    name = "resultsScraper"

    allowed_domains = [urlparse(url).netloc for url in start_urls]

    # Classification file is for keeping track of what each url has been classified as
    modified_start_url = url_to_short_file_name(start_urls[0])
    classification_file_path = 'scraped_data/classification/{}_classification_file_urls.csv'.format(modified_start_url)
    classification_file = open(classification_file_path, 'w')

    isResultsPageLogger = logging.getLogger('isResultsPage')
    isResultsPageLogger.setLevel(logging.CRITICAL)
    isIndexPageLogger = logging.getLogger('isIndexPage')
    isIndexPageLogger.setLevel(logging.CRITICAL)
    dupefilterLogger = logging.getLogger('scrapy.dupefilters')
    dupefilterLogger.setLevel(logging.CRITICAL)

    def __init__(self):
        self.rate_limit = True
        super().__init__()

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding parsing procedure
        :param response:
        :return:
        """
        # print("processing: {}".format(response.url))
        if self.initial_page_filter(response):
            if self.is_captcha_page(response.url, response):
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

    def process_question_answer_page(self, response):
        """
        For responses identified as results pages, we extract the question/answer posts of the page
        :param response:
        :return: list of Q/A pairs
        """
        # All posts on page (might be posts on other pages though)
        self.results_page_count += 1
        if self.isResultsPage.is_pertinent:
            self.classification_file.write("results, {}\n".format(response.url))
            logging.info('results: {}'.format(response.url))
            print("results: {}".format(response.url))

            # Filters
            if not self.is_page_relevant(response):  # check we are talking about the right thing
                return None
            if not self.page_contains_answers(response):
                return None

            # Process posts
            posts = self.isResultsPage.parsed_text_content
            question = posts[0]
            question_answer_list = []
            question_answer = QuestionAnswer()
            question_answer = self.fill_question(response, question_answer, question)

            # Cycle through posts and build Q/A pairs
            posts = [post for post in posts[1:] if len(post) > 0]
            posts = self.filter_posts(response, posts)  # TODO implement function
            for answer_number in range(len(posts)):
                question_answer = self.fill_answer(response, question_answer, posts[answer_number])
                question_answer_list.append(question_answer)
            return question_answer_list
        else:
            self.classification_file.write("results (off topic), {}\n".format(response.url))
            logging.info('results (off topic): {}'.format(response.url))
            print("results (off topic): {}".format(response.url))

    def process_index_page(self, response):
        """
        For responses identified as index pages, we extract the link to follow
        N.B. this function is not currently used in crawler
        :return:
        """
        self.index_page_count += 1
        if self.isIndexPage.is_pertinent:
            logging.info('index: {}'.format(response.url))
            print('index: {}'.format(response.url))
            self.classification_file.write("index, {}\n".format(response.url))
            result_links = self.isIndexPage.result_links
            pagination_links = self.isIndexPage.pagination_links
            for result_link in result_links:
                yield SplashRequest(url=result_link, callback=self.identify_and_parse_page, args={'wait': 1})
            for pagination_link in pagination_links:
                yield SplashRequest(url=pagination_link, callback=self.identify_and_parse_page, args={'wait': 1})
            time.sleep(self.new_index_page_pause_time)
        else:
            logging.info('index (off topic): {}'.format(response.url))
            print('index (off topic): {}'.format(response.url))
            self.classification_file.write("index (off topic), {}\n".format(response.url))


    ### Q/A parsing functions

    def fill_question(self, response, question_answer, question):
        """
        :param response:
        :param question_answer: scrapy question_answer item to be filled
        :param question: parsed question content to put in question_answer item
        :return: question_answer item filled with question
        """
        question_answer['source_url'] = response.url
        question_answer['question_body'] = question['body']
        if question['author']:
            question_answer['question_author'] = {'author_id': '{}_{}'.format(urlparse(self.start_urls[0]).netloc, question['author']),
                                              'author_name': question['author']}
        if question['date']:
            question_answer['question_date'] = date_to_solr_format(question['date'])
        return question_answer

    def fill_answer(self, response, question_answer, answer):
        """
        
        :param response:
        :param question_answer: scrapy question_answer item to be filled
        :param answer: parsed answer content to put in question_answer item
        :return: question_answer item filled with answer
        """
        question_answer['answer_body'] = answer['body']
        if answer['author']:
            question_answer['answer_author'] = {
                'author_id': '{}_{}'.format(urlparse(self.start_urls[0]).netloc, answer['author']),
                'author_name': answer['author']}
        if answer['date']:
            question_answer['answer_date'] = date_to_solr_format(answer['date'])

        return question_answer

    ### Filter functions

    def is_page_relevant(self, response):
        """
        Check product is in tags (Not yet implemented)
        :param response:
        :return:
        """
        return True

    def filter_posts(self, response, posts):
        """
        Return only pertinent Q/A pairs (Not yet implemented)
        :param response:
        :param posts:
        :return:
        """
        return posts


