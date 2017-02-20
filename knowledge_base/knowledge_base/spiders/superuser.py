# -*- coding: utf-8 -*-
import scrapy
# from scrapy.loader import ItemLoader

from ..items import QuestionAnswer
from cssselect import GenericTranslator, SelectorError


class SuperuserSpider(scrapy.Spider):
    name = "superuser"
    allowed_domains = ["superuser.com"]
    start_urls = ['http://superuser.com/questions/56215/outlook-restore',
                  'http://superuser.com/questions/348750/outlook-reminders-not-appearing',
                  'http://superuser.com/questions/781717/outlook-2007-how-to-search-filter-content-of-a-search-folder/781731',
                  'http://superuser.com/questions/696979/removing-default-outlook-account-in-windows-mail',
                  'http://superuser.com/questions/273217/completely-reset-outlook-2007-to-first-run',
                  'http://superuser.com/questions/941455/upgrade-from-ms-outlook-2003-to-ms-outlook-2013-how-to-migrate-custom-views-an',
                  'http://superuser.com/questions/848948/redirecting-outlook-meeting-request',
                  'http://superuser.com/questions/934323/where-are-my-pst-files-for-outlook-2013',
                  'http://superuser.com/questions/98229/outlook-ignorelist',
                  'http://superuser.com/questions/56215/outlook-restore',
                  'http://superuser.com/questions/51942/outlook-sharing',
                  'http://superuser.com/questions/1000283/outlook-archiving',
                  'http://superuser.com/questions/180343/import-outlook-2007-messages-to-outlook-express',
                  'http://superuser.com/questions/387630/outlook-2003-outlook-2010-migration',
                  'http://superuser.com/questions/49409/outlook-structure',
                  'http://superuser.com/questions/62824/outlook-automation']
    gt = GenericTranslator()

    def parse(self, response):
        """
        @TODO avoid mixing css and xpath
        @TODO: write function that takes css class as list and converts to xpath
        @TODO: put the split in try catch
        @TODO: make sure int conversion handles exceptions
        @TODO: handle exceptions if list index doesn't exist (or improve xpaths ? )
        @TODO: check answer exists before scraping
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

