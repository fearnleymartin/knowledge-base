# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from datetime import datetime
from bs4 import BeautifulSoup
import re
from .master import MasterSpider
from ..utils import date_to_solr_format


class MacRumorsSpider(MasterSpider):
    """
    Hardcoded crawler for macrumors.com
    """
    name = "macrumors"
    allowed_domains = ["macrumors.com"]
    custom_settings = {'DOWNLOAD_DELAY': 0,
                       'LOG_FILE': 'logs/{}_log.txt'.format(name)
                       }

    product_index_dict = \
        {
            'iPhone': 'https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/',
            'iPad': 'https://forums.macrumors.com/forums/ipad-tips-help-and-troubleshooting.151/'
        }

    product = 'iPhone'
    start_urls = [product_index_dict[product]]

    def __init__(self):
        self.rate_limit = False
        super().__init__()

    allow = ('threads', 'forum')
    deny = ('members')
    restrict_xpaths = (MasterSpider.gt.css_to_xpath('.listBlock'),
                       MasterSpider.gt.css_to_xpath('.PageNav'))

    def process_question_answer_page(self, response):
        """
        Once we have identified this is a results page,
        We extract the information
        :param response:
        :return: list of Q/A pairs
        """

        # Filters
        if not self.is_page_relevant(response):  # check we are talking about the right thing
            return None
        if not self.page_contains_answers(response):
            return None


        # Process posts
        posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
        question_answer_list = []
        question_answer = QuestionAnswer()
        question_answer = self.fill_question(response, question_answer)

        # Cycle through posts and build Q/A pairs
        posts = [BeautifulSoup(post).text.replace("\t", "").replace("\n", "").replace("\u00a0", "") for post in posts]
        posts = [post for post in posts[1:] if len(post) > 0]
        posts = self.filter_posts(response, posts)  # TODO implement function
        for answer_number in range(len(posts)):
            question_answer = self.fill_question(response, question_answer)
            question_answer_list.append(question_answer)
        return question_answer_list

    ### Q/A parsing functions

    def fill_question(self, response, question_answer):
        """
        :param response:
        :param question_answer:
        :return:
        """
        question_answer['source_url'] = response.url
        question_answer['question_title'] = response.xpath(
            '//*[@id="content"]/div/div/div[2]/div/div[1]/div/h1/text()').extract_first()
        question_answer['question_body'] = BeautifulSoup(response.xpath(self.gt.css_to_xpath('.messageText')).extract_first()).text.replace("\t", "").replace("\n", "").replace("\u00a0", "")
        tags = list(set(
            response.xpath('//*[@id="content"]/div/div/div[1]/nav/fieldset/span/span[3]/a/span/text()').extract()))
        tags = [tag.lower() for tag in tags]
        question_answer['question_tags'] = tags

        author_name = response.xpath(self.gt.css_to_xpath('.username') + '/text()').extract_first()
        question_answer['question_author'] = {'author_id': '{}_{}'.format(self.allowed_domains[0], author_name),
                                              'author_name': author_name}

        mac_rumors_date_format = '%b %d, %Y at %I:%M %p'
        mac_rumors_date_format2 = '%b %d, %Y'

        date = response.xpath(self.gt.css_to_xpath('.messageDetails .DateTime') + '/@data-datestring').extract_first()
        if date:
            date = re.sub('^0|(?<= )0', '', date)
            question_answer['question_date'] = date_to_solr_format(datetime.strptime(date, mac_rumors_date_format2))
        else:
            date = response.xpath(
                self.gt.css_to_xpath('.messageDetails .DateTime') + '/@title').extract_first()
            if date:
                date = re.sub('^0|(?<= )0', '', date)
                question_answer['question_date'] = date_to_solr_format(datetime.strptime(date, mac_rumors_date_format))
            else:
                pass

        return question_answer

    def fill_answer(self, response, question_answer, answer_number):
        """
        :param response:
        :param question_answer:
        :param answer_number:
        :return:
        """
        posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
        posts = [BeautifulSoup(post).text.replace("\t", "").replace("\n", "").replace("\u00a0", "") for post in posts]
        posts = [post for post in posts[1:] if len(post) > 0]

        question_answer['answer_body'] = posts[answer_number]

        return question_answer

    ### Filter functions

    def is_page_relevant(self, response):
        """
        Check product is in tags
        :param response:
        :return:
        """
        tags = list(set(
            response.xpath('//*[@id="content"]/div/div/div[1]/nav/fieldset/span/span[3]/a/span/text()').extract()))
        tags = [tag.lower() for tag in tags]
        if self.product.lower() not in tags:  # check we are talking about the right thing
            return False
        else:
            return True

    def page_contains_answers(self, response):
        """

        :param response:
        :return: true if page has more than one post
        """
        posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
        if len(posts) < 1:  # Check there are posts with answers
            return False
        else:
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

    ### Page identification functions

    def is_results_page(self, url, response=None):
        # @TODO tidy up types
        if type(url) is not str:
            url = url.url
        return "threads" in url

    def is_index_page(self, url, response=None):
        """
        :param url:
        :return: True if url is a page that list search results
        """
        # TODO: generalise
        return "forums.macrumors.com/forums" in url

    def is_captcha_page(self, url, response=None):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return "nocaptcha" in url



