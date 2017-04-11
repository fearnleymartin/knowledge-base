# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
# from datetime import datetime
# from bs4 import BeautifulSoup
# import re
from .master import MasterSpider
from ..utils import date_to_solr_format, url_to_short_file_name
import logging
import scrapy
from scrapy_splash import SplashRequest


class resultsScraper(MasterSpider):
    """
    This spider will crawl any webpage and extract Q/A pairs to a jsonlines file
    It works by classifying the pages into index pages / results pages / other and parsing results pages with an algorithm using the html structure of the page
    Specify the start_url and the allowed domain
    """
    isResultsPageLogger = logging.getLogger('isResultsPage')
    isResultsPageLogger.propagate = False
    isIndexPageLogger = logging.getLogger('isIndexPage')
    isIndexPageLogger.propagate = False

    name = "resultsScraper"
    product = "Unknown"

    allowed_domains = ["macrumors.com", "microsoft.com", "stackoverflow.com", "forum.mailenable.com"]
    # TODO: Bug : Not overriding main settings
    custom_settings = {'DOWNLOAD_DELAY': 0,
                       'LOG_FILE': 'logs/{}_log.txt'.format(name)

                       }


    # start_urls = ['https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/']
    # start_urls = ['http://stackoverflow.com/questions/tagged/regex']
    # start_urls = [
    #     'https://answers.microsoft.com/en-us/search/search?SearchTerm=powerpoint&IsSuggestedTerm=false&tab=&CurrentScope.ForumName=msoffice&CurrentScope.Filter=msoffice_powerpoint-mso_win10-mso_o365b&ContentTypeScope=&auth=1#/msoffice/msoffice_powerpoint-mso_win10-mso_o365b//1']
    start_urls = ['http://forum.mailenable.com/viewforum.php?f=2&sid=805e9ea1611daf70a515c16519f48513']

    # TODO: improve parsing with regex
    # Classification file is for keeping track of what each url has been classified as
    modified_start_url = url_to_short_file_name(start_urls[0])
    classification_file_path = 'scraped_data/classification/{}_classification_file.csv'.format(modified_start_url)
    classification_file = open(classification_file_path, 'w')

    def __init__(self):
        self.rate_limit = False
        super().__init__()

    rules = ()

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
                return self.process_index_page(response)
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


    def process_question_answer_page(self, response):
        """
        Once we have identified this is a results page,
        We extract the information
        :param response:
        :return: list of Q/A pairs
        """
        # TODO: implement going through pagination of forums responses
        # All posts on page (might be posts on other pages though, )

        self.results_page_count += 1
        self.classification_file.write("results, {}\n".format(response.url))
        logging.info('results: {}'.format(response.url))
        print("results: {}".format(response.url))
        # Filters
        if not self.is_page_relevant(response):  # check we are talking about the right thing
            return None
        if not self.page_contains_answers(response):
            return None


        # Process posts
        posts = self.isResultsPage.text_content
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

    def process_index_page(self, response):
        """
        At the moment just logs that we have an index page, and pauses
        :return:
        """
        logging.info('index: {}'.format(response.url))
        print('index: {}'.format(response.url))
        self.classification_file.write("index, {}\n".format(response.url))
        self.index_page_count += 1
        result_links = self.isIndexPage.result_links
        pagination_links = self.isIndexPage.pagination_links
        meta = {'splash': {'args': {'html': 1}}}
        for result_link in result_links:
            # print("result link", result_link)
            # yield scrapy.Request(url=result_link, callback=self.identify_and_parse_page, meta=meta)
            yield SplashRequest(url=result_link, callback=self.identify_and_parse_page, args={'wait': 0.5})
        for pagination_link in pagination_links:
            yield SplashRequest(url=pagination_link, callback=self.identify_and_parse_page, args={'wait': 0.5})
        # time.sleep(self.new_index_page_pause_time)

    ### Q/A parsing functions

    def fill_question(self, response, question_answer, question):
        """
        @TODO remove repetition of tags
        :param response:
        :param question_answer:
        :return:
        """
        question_answer['source_url'] = response.url

        # question_answer['question_title'] = response.xpath(
        #     '//*[@id="content"]/div/div/div[2]/div/div[1]/div/h1/text()').extract_first()

        question_answer['question_body'] = question

        # BeautifulSoup(response.xpath(self.gt.css_to_xpath('.messageText')).extract_first()).text.replace("\t", "").replace("\n", "").replace("\u00a0", "")

        # tags = list(set(
        #     response.xpath('//*[@id="content"]/div/div/div[1]/nav/fieldset/span/span[3]/a/span/text()').extract()))
        # tags = [tag.lower() for tag in tags]
        # question_answer['question_tags'] = tags

        # TODO: remove in general case
        author_name = response.xpath(self.gt.css_to_xpath('.username') + '/text()').extract_first()
        question_answer['question_author'] = {'author_id': '{}_{}'.format(self.allowed_domains[0], author_name),
                                              'author_name': author_name}

        # mac_rumors_date_format = '%b %d, %Y at %I:%M %p'
        # mac_rumors_date_format2 = '%b %d, %Y'

        # date = response.xpath(self.gt.css_to_xpath('.messageDetails .DateTime') + '/@data-datestring').extract_first()
        # if date:
        #     date = re.sub('^0|(?<= )0', '', date)
        #     question_answer['question_date'] = date_to_solr_format(datetime.strptime(date, mac_rumors_date_format2))
        # else:
        #     date = response.xpath(
        #         self.gt.css_to_xpath('.messageDetails .DateTime') + '/@title').extract_first()
        #     if date:
        #         date = re.sub('^0|(?<= )0', '', date)
        #         question_answer['question_date'] = date_to_solr_format(datetime.strptime(date, mac_rumors_date_format))
        #     else:
        #         pass

        return question_answer

    def fill_answer(self, response, question_answer, answer):
        """
        @TODO: remove repetition of posts
        :param response:
        :param question_answer:
        :param answer:
        :return:
        """
        # posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
        # posts = [BeautifulSoup(post).text.replace("\t", "").replace("\n", "").replace("\u00a0", "") for post in posts]
        # posts = [post for post in posts[1:] if len(post) > 0]

        question_answer['answer_body'] = answer

        return question_answer

    ## Helper functions

    ### Filter functions

    def is_page_relevant(self, response):
        """
        Check product is in tags
        :param response:
        :return:
        """
        return True

    def page_contains_answers(self, response):
        """

        :param response:
        :return: true if page has more than one post
        """
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

    # def is_results_page(self, url, response=None):
    #     # @TODO tidy up types
    #     super().is_results_page(url, response)
    #
    # def is_index_page(self, url, response=None):
    #     """
    #     :param url:
    #     :return: True if url is a page that list search results
    #     """
    #     super().is_index_page(url, response)
    #
    # def is_captcha_page(self, url, response=None):
    #     """
    #     @TODO generalise
    #     :param url:
    #     :return: True if request has been redirected to captcha
    #     """
    #     super().is_captcha_page(url, response)


