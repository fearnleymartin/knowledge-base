# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
from .master import MasterSpider


class SuperUserSpider(MasterSpider):
    """
    Will generalise to Q/A site spider
    """
    name = "superuser"
    allowed_domains = ["superuser.com"]
    custom_settings = {'DOWNLOAD_DELAY': 0.45,
                       'LOG_FILE': 'logs/superuser_log.txt'
                       }

    def __init__(self):
        self.rate_limit = True
        super().__init__()

    product = 'outlook'

    start_urls = ['http://superuser.com/search?q={}'.format(product)]

    rules = (
        # @TODO generalise
        Rule(LinkExtractor(allow=('superuser.com/search', 'superuser.com/questions/'),
                           deny=('superuser.com/questions/tagged', 'superuser.com/questions/ask', 'submit', 'answertab'),
                           restrict_xpaths=(MasterSpider.gt.css_to_xpath('.result-link'), MasterSpider.gt.css_to_xpath('.pager'))),
             callback="identify_and_parse_page",
             follow=True),
    )


    def identify_and_parse_page(self, response):
        """
        @TODO: put the split in try catch
        @TODO: make sure int conversion handles exceptions
        @TODO: handle exceptions if list index doesn't exist (or improve xpaths ? )
        @TODO: implement go to next search page
        N.B. only returns first answer
        :param response:
        :return:
        """

        # check whether search page or question page
        if self.is_index_page(response.url):  # if search page, extract link and next page
            self.process_index_page(response)
        elif self.is_captcha_page(response.url):
            self.process_captcha(response)
        else:  # if question page, parse post
            items = self.parse_items(response)
            return items

    def is_index_page(self, url):
        """
        @TODO: generalise
        :param url:
        :return: True if url is a page that list search results
        """
        return "superuser.com/search" in url

    def is_captcha_page(self, url):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return "nocaptcha" in url

    def parse_items(self, response):
        # check whether answer exists
        if response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract_first() is None:
            return None  # no answer exists
        else:
            answers = response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract()
            question_answer_list = []
            for answer_number in range(len(answers)):
                question_answer = self.fill_question(response)
                question_answer = self.fill_answer(response, question_answer, answer_number)
                question_answer_list.append(question_answer)
            return question_answer_list

    def fill_question(self, response):
        question_answer = QuestionAnswer()
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
            question_answer['question_date'] = str(datetime.strptime(response.xpath(
                self.gt.css_to_xpath('.owner .user-action-time .relativetime') + '/text()').extract_first(),
                                                                     se_date_format))
        except ValueError:
            question_answer['question_date'] = str(datetime.strptime(response.xpath(
                self.gt.css_to_xpath('.owner .user-action-time .relativetime') + '/text()').extract_first(),
                                                                     se_date_format_curr_year))
        return question_answer

    def fill_answer(self, response, question_answer, answer_number):
        """
        @TODO improve so not doing operation multiple times for question
        @TODO break components down into functions
        :param response:
        :param tags:
        :param question:
        :param answer:
        :return:
        """
        question_answer['answer_body'] = BeautifulSoup(
            response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract()[answer_number]).text
        question_answer['answer_upvotes'] = int(response.xpath(
            '//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract()[answer_number+1])
        # slightly more complicated
        # question_answer['answer_accepted'] = response.xpath(
        #     self.gt.css_to_xpath('.vote-accepted-on') + '/text()').extract()[answer_number] == 'accepted'
        return question_answer