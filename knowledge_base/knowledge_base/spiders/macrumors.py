# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
import re
from .master import MasterSpider
from ..utils import date_to_solr_format


class MacRumorsSpider(MasterSpider):
    """
    Will generalise to forum spider
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

    # start_urls = ['https://forums.macrumors.com/threads/switching-from-pc-to-mac-formatted.2033690/#post-24327208']

    def __init__(self):
        self.rate_limit = False
        super().__init__()

    # @TODO: only extract relevant pages (e.g. has replies)
    rules = (
        Rule(LinkExtractor(allow=('threads','forum'),
                           deny=('members'),
                           restrict_xpaths=(MasterSpider.gt.css_to_xpath('.listBlock'),
                                            MasterSpider.gt.css_to_xpath('.PageNav'))
                           ),
             callback="identify_and_parse_page",
             follow=True),
    )



    def is_index_page(self, url):
        """
        @TODO: generalise
        :param url:
        :return: True if url is a page that list search results
        """
        return "forums.macrumors.com/forums" in url

    def is_captcha_page(self, url):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return "nocaptcha" in url

    def process_question_answer_page(self, response):
        """
        @TODO: implement going through pagination of forums responses
        :param response:
        :return:
        """

        # All posts on page (might be posts on other pages though, )
        # @TODO abstract  to is_page_relevant() and also check number of posts here
        tags = list(set(
                response.xpath('//*[@id="content"]/div/div/div[1]/nav/fieldset/span/span[3]/a/span/text()').extract()))
        tags = [tag.lower() for tag in tags]
        if self.product.lower() not in tags:  # check we are talking about the right thing
            return None
        else:
            posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
            if len(posts) < 1:  # Check there are posts with answers
                return None
            else:
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

    def fill_question(self, response, question_answer):
        """
        @TODO remove repetition of tags
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
        @TODO: remove repetition of posts
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

    def filter_posts(self, response, posts):
        """
        TODO: implement
        Return only pertinant Q/A pairs
        :param response:
        :param posts:
        :return:
        """
        return posts

