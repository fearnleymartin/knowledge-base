# -*- coding: utf-8 -*-
from scrapy_splash import SplashRequest

from ..items import QuestionAnswer
from datetime import datetime
from bs4 import BeautifulSoup
from .master import MasterSpider
from ..utils import date_to_solr_format
import logging
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


class SuperUserSpider(MasterSpider):
    """
    Will generalise to Q/A site spider
    """
    name = "superuser"
    allowed_domains = ["superuser.com"]
    custom_settings = {'DOWNLOAD_DELAY': 0,
                       'LOG_FILE': 'logs/superuser_log.txt'
                       }

    def __init__(self):
        self.rate_limit = False
        super().__init__()
        self.duplicate_count = 0

    product = 'outlook'
    product = 'ubuntu'
    # start_urls = ['http://superuser.com/search?q={}'.format(product)]

    start_urls = ['https://superuser.com/questions/tagged/{}'.format(product)]
    # start_urls = ['https://superuser.com/questions/743662/what-are-system-active-and-boot-partitions-in-terms-of-microsoft']

    allow = ('superuser.com/search', 'superuser.com/questions/', )
    deny = ('superuser.com/questions/ask', 'submit', 'answertab', '/users/',
            'superuser.com/help','superuser.com/tags','superuser.com/tour','superuser.com/users')
    restrict_xpaths = (MasterSpider.gt.css_to_xpath('.result-link'), MasterSpider.gt.css_to_xpath('.pager'),
                       MasterSpider.gt.css_to_xpath('.question-hyperlink'))

    modified_start_url = start_urls[0].replace('https://', '').replace('http://', '').replace('/', '_').replace('=', '').replace('?','')[:100]
    classification_file_path = 'scraped_data/classification/{}_classification_file2.csv'.format(modified_start_url)
    classification_file = open(classification_file_path, 'w')

    rules = (
        Rule(LinkExtractor(allow=allow,  # Allow index and results pages
                           deny=deny,  # Other pages
                           restrict_xpaths=restrict_xpaths),  # Pagination, results pages
             callback="identify_and_parse_page",
             process_links="process_links",
             follow=True),
    )

    def process_question_answer_page(self, response):
        """
        Extracts Q/A pairs and parses them to scrapy's items pipeline
        :param response: question_answer item object
        :return:
        """
        # TODO: implement going through pagination of forums responses
        # All posts on page (might be posts on other pages though, )

        self.results_page_count += 1
        self.classification_file.write("results, {}\n".format(response.url))
        logging.info('results: {}'.format(response.url))
        print("results: {}".format(response.url))

        # Filters
        if not self.page_contains_answers(response):
            return None

        # Process posts
        question_answer_list = []
        question_answer = QuestionAnswer()
        question_answer = self.fill_question(response, question_answer)
        # cycle through answers and build Q/A pairs
        answers = response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract()
        for answer_number in range(len(answers)):
            question_answer_copy = question_answer.copy()
            question_answer_copy = self.fill_answer(response, question_answer_copy, answer_number)
            question_answer_list.append(question_answer_copy)
        return question_answer_list

    ### Q/A parsing functions

    def fill_question(self, response, question_answer):
        """
        Extracts information related to the question
        :param response:
        :return: question_answer pair with question information filled in
        """
        question_answer['source_url'] = response.url

        question_answer['question_title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        question_answer['question_body'] = BeautifulSoup(
            response.xpath(self.gt.css_to_xpath('.postcell .post-text')).extract_first()).text
        question_answer['question_tags'] = list(set(
            response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " post-tag ")]/text()').extract()))
        # would like to specify the hierarchy of the css tags
        question_answer['question_upvotes'] = int(response.xpath(
            '//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract_first())
        question_answer['question_view_count'] = int(
            response.xpath(self.gt.css_to_xpath('#qinfo .label-key') + '/b/text()').extract()[1].split(' ')[0])

        author_name = response.xpath(
            self.gt.css_to_xpath('.owner .user-details') + '/a/text()').extract_first()
        question_answer['question_author'] = {'author_id': '{}_{}'.format(self.allowed_domains[0], author_name),
                                              'author_name': author_name}

        se_date_format = '%b %d \'%y at %H:%M'  # if date not current year
        se_date_format_curr_year = '%b %d at %H:%M'  # if date current year
        try:
            try:
                question_answer['question_date'] = date_to_solr_format(datetime.strptime(response.xpath(
                    self.gt.css_to_xpath('.owner .user-action-time .relativetime') + '/text()').extract_first(),
                                                                         se_date_format))
            except ValueError:
                question_answer['question_date'] = date_to_solr_format(datetime.strptime(response.xpath(
                    self.gt.css_to_xpath('.owner .user-action-time .relativetime') + '/text()').extract_first(),
                                                                         se_date_format_curr_year))
        except (ValueError, TypeError):
            pass
        # Look for duplicates
        duplicate_url = response.xpath(self.gt.css_to_xpath('.question-originals-of-duplicate')+'/ul/li/a/@href').extract()
        if duplicate_url:
            print('duplicate question')
            self.duplicate_count += 1
            print('duplicate question count: {}'.format(self.duplicate_count))
            print(duplicate_url)
            self.logger.info('duplicate url: {}'.format(duplicate_url))
            question_answer['question_original_url'] = duplicate_url
            # TODO: issue request for duplicate url
            # yield SplashRequest(url=response.url, callback=self.identify_and_parse_page, args={'wait': 0.5})

        return question_answer

    def fill_answer(self, response, question_answer, answer_number):
        """
        @TODO break components down into functions
        :param response:
        :param question_answer: question_answer item object
        :param answer_number: position of answer in page
        :return: question_answer item object with answer information filled in corresponding to answer number
        """
        question_answer['answer_body'] = BeautifulSoup(
            response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract()[answer_number]).text
        question_answer['answer_upvotes'] = int(response.xpath(
            '//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract()[answer_number+1])
        # slightly more complicated
        # question_answer['answer_accepted'] = response.xpath(
        #     self.gt.css_to_xpath('.vote-accepted-on') + '/text()').extract()[answer_number] == 'accepted'
        return question_answer

    ### Filter functions

    def page_contains_answers(self, response):
        if response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract_first() is None:
            return False  # no answer exists
        else:
            return True

    ### Page identification functions

    def is_results_page(self, url, response=None):
        # @TODO tidy up types
        if type(url) is not str:
            url = url.url
        return "superuser.com/questions/" in url

    def is_index_page(self, url, response=None):
        """
        @TODO: generalise
        :param url:
        :return: True if url is a page that list search results
        """
        return "superuser.com/search" in url or "superuser.com/questions/tagged" in url

    def is_captcha_page(self, url, response=None):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return "nocaptcha" in url