# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from bs4 import BeautifulSoup
import re
from .master import MasterSpider


class MacRumorsSpider(MasterSpider):
    """
    Will generalise to forum spider
    """
    name = "macrumors"
    allowed_domains = ["macrumors.com"]
    custom_settings = {'DOWNLOAD_DELAY': 0.45,
                       'LOG_FILE': 'logs/superuser_log.txt'
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


    def identify_and_parse_page(self, response):
        """
        @TODO: put the split in try catch
        @TODO: make sure int conversion handles exceptions
        @TODO: handle exceptions if list index doesn't exist (or improve xpaths ? )
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
        return "forums.macrumors.com/forums" in url

    def is_captcha_page(self, url):
        """
        @TODO generalise
        :param url:
        :return: True if request has been redirected to captcha
        """
        return "nocaptcha" in url

    def parse_items(self, response):
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
                posts = [BeautifulSoup(post).text.replace("\t", "").replace("\n", "").replace("\u00a0", "") for post in posts]
                question = posts[0]
                question_answer_list = []
                for answer in [post for post in posts[1:] if len(post) > 0]:
                    question_answer = self.fill_question_answer(response, tags, question, answer)
                    question_answer_list.append(question_answer)
                return question_answer_list



    def fill_question_answer(self, response, tags, question, answer):
        """
        @TODO improve so not doing operation multiple times for question
        @TODO break components down into functions
        :param response:
        :param tags:
        :param question:
        :param answer:
        :return:
        """

        question_answer = QuestionAnswer()
        question_answer['source_url'] = response.url

        question_answer['question_title'] = response.xpath(
            '//*[@id="content"]/div/div/div[2]/div/div[1]/div/h1/text()').extract_first()

        question_answer['question_body'] = question
        question_answer['question_tags'] = tags

        author_name = response.xpath(self.gt.css_to_xpath('.username') + '/text()').extract_first()
        question_answer['question_author'] = {'author_id': '{}_{}'.format(self.allowed_domains[0], author_name),
                                              'author_name': author_name}

        mac_rumors_date_format = '%b %d, %Y at %I:%M %p'
        mac_rumors_date_format2 = '%b %d, %Y'

        date = response.xpath(self.gt.css_to_xpath('.messageDetails .DateTime') + '/@data-datestring').extract_first()
        if date:
            date = re.sub('^0|(?<= )0', '', date)
            question_answer['question_date'] = str(datetime.strptime(date, mac_rumors_date_format2))
        else:
            date = response.xpath(
                self.gt.css_to_xpath('.messageDetails .DateTime') + '/@title').extract_first()
            if date:
                date = re.sub('^0|(?<= )0', '', date)
                question_answer['question_date'] = str(datetime.strptime(date, mac_rumors_date_format))
            else:
                pass

        # To include other data eventually
        # question_answer['answers'] = [post for post in posts[1:] if len(post) > 0]

        question_answer['answer_body'] = answer

        return question_answer