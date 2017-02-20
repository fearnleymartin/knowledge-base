# -*- coding: utf-8 -*-
import scrapy
# from scrapy.loader import ItemLoader

from ..items import QuestionAnswer
from cssselect import GenericTranslator, SelectorError


class SuperuserSpider(scrapy.Spider):
    name = "superuser"
    allowed_domains = ["superuser.com"]
    start_urls = ['http://superuser.com/questions/56215/outlook-restore']
    gt = GenericTranslator()

    def parse(self, response):
        """
        @TODO avoid mixing css and xpath
        @TODO: write function that takes css class as list and converts to xpath
        @TODO: put the split in try catch
        @TODO: make sure int conversion handles exceptions
        @TODO: handle exceptions if list index doesn't exist (or improve xpaths ? )
        N.B. only returns first answer
        :param response:
        :return:
        """
        question_answer = QuestionAnswer()
        question_answer['question_title'] = response.xpath('//*[@id="question-header"]/h1/a/text()').extract_first()
        question_answer['question_body'] = response.xpath(self.gt.css_to_xpath('.postcell .post-text') + '/p/text()').extract()
        question_answer['question_tags'] = response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " post-tag ")]/text()').extract()
        # would like to specify the hierarchy of the css tags
        question_answer['question_upvotes'] = int(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract_first())
        question_answer['question_view_count'] = int(response.xpath(self.gt.css_to_xpath('#qinfo .label-key') + '/b/text()').extract()[1].split(' ')[0])
        # yield question_answer

        # answer = Answer()
        question_answer['answer_body'] = response.xpath(self.gt.css_to_xpath('.answercell .post-text') + '/p/text()').extract()
        question_answer['answer_upvotes'] = int(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " vote-count-post ")]/text()').extract()[1])
        question_answer['answer_accepted'] = response.xpath(self.gt.css_to_xpath('.vote-accepted-on')+'/text()').extract_first() == 'accepted'
        yield question_answer

