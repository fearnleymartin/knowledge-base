# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
from cssselect import GenericTranslator
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import logging
from bs4 import BeautifulSoup



class SuperuserSpider(CrawlSpider):
    name = "superuser"
    allowed_domains = ["superuser.com"]

    start_urls = ['http://superuser.com/search?q=outlook']
    gt = GenericTranslator()

    rules = (
        Rule(LinkExtractor(allow=('superuser.com/search', 'superuser.com/questions/'),
                           deny=('superuser.com/questions/tagged', 'superuser.com/questions/ask', 'submit', 'answertab'),
                           restrict_xpaths=(gt.css_to_xpath('.result-link'), gt.css_to_xpath('.pager'))),
             callback="parse_items",
             follow=True),
    )

    def parse_items(self, response):
        """
        @TODO: put the split in try catch
        @TODO: make sure int conversion handles exceptions
        @TODO: handle exceptions if list index doesn't exist (or improve xpaths ? )
        @TODO: check answer exists before scraping
        @TODO: handle captchas
        @TODO: implement go to next search page
        N.B. only returns first answer
        :param response:
        :return:
        """

        # check whether search page or question page
        if "superuser.com/search" in response.url:  # if search page, extract link and next page
            logging.info('new search page')
            logging.info(response.url)
            pass
        elif "nocaptcha" in response.url:
            logging.info('captcha problem')
        else:  # if question page, parse post

            # check whether answer exists
            if response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract_first() is None:
                pass  # no answer exists
            else:
                question_answer = QuestionAnswer()
                question_answer['question_title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
                question_answer['question_body'] = BeautifulSoup(response.xpath(self.gt.css_to_xpath('.postcell .post-text')).extract_first()).text
                question_answer['question_tags'] = list(set(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " post-tag ")]/text()').extract()))
                # would like to specify the hierarchy of the css tags
                question_answer['question_upvotes'] = int(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract_first())
                question_answer['question_view_count'] = int(response.xpath(self.gt.css_to_xpath('#qinfo .label-key') + '/b/text()').extract()[1].split(' ')[0])
                question_answer['question_author'] = response.xpath(self.gt.css_to_xpath('.owner .user-details')+'/a/text()').extract_first()
                se_date_format = '%b %d \'%y at %H:%M'
                question_answer['question_date'] = str(datetime.strptime(response.xpath(self.gt.css_to_xpath('.owner .user-action-time .relativetime')+'/text()').extract_first(), se_date_format))


                question_answer['answer_body'] = BeautifulSoup(response.xpath(self.gt.css_to_xpath('.answercell .post-text')).extract_first()).text
                question_answer['answer_upvotes'] = int(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract()[1])
                question_answer['answer_accepted'] = response.xpath(self.gt.css_to_xpath('.vote-accepted-on')+'/text()').extract_first() == 'accepted'
                yield question_answer



