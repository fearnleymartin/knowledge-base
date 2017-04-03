# -*- coding: utf-8 -*-

from ..items import QuestionAnswer
# from datetime import datetime
# from bs4 import BeautifulSoup
# import re
from .master import MasterSpider
# from ..utils import date_to_solr_format
import logging


class resultsScraper(MasterSpider):
    """
    Will generalise to forum spider
    """
    isResultsPageLogger = logging.getLogger('isResultsPage')
    isResultsPageLogger.propagate = False
    isIndexPageLogger = logging.getLogger('isIndexPage')
    isIndexPageLogger.propagate = False

    name = "resultsScraper"
    product = "Unknown"

    allowed_domains = ["macrumors.com", "microsoft.com", "stackoverflow.com"]
    custom_settings = {'DOWNLOAD_DELAY': 0,
                       'LOG_FILE': 'logs/{}_log.txt'.format(name)

                       }


    start_urls = ['https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/']
    start_urls = ['http://stackoverflow.com/questions/tagged/regex']
    # start_urls = [
    #     'https://answers.microsoft.com/en-us/search/search?SearchTerm=powerpoint&IsSuggestedTerm=false&tab=&CurrentScope.ForumName=msoffice&CurrentScope.Filter=msoffice_powerpoint-mso_win10-mso_o365b&ContentTypeScope=&auth=1#/msoffice/msoffice_powerpoint-mso_win10-mso_o365b//1']

    # TODO: improve parsing with regex
    url_path = start_urls[0].replace('https://', '').replace('http://','').replace('/', '_')[:100]
    print(url_path)
    classification_file_path = 'scraped_data/classification/{}_classification_file2.csv'.format(url_path)
    print(classification_file_path)
    classification_file = open(classification_file_path, 'w')

    # TODO cheating for macrumors: to remove


    def __init__(self):
        self.rate_limit = False
        super().__init__()

    def identify_and_parse_page(self, response):
        """
        Identifies page type (index page, captcha, results page)
        and runs corresponding parsing procedure
        :param response:
        :return:
        """
        # print("call back response is not none: {}".format(response is not None))
        # print("processing: {}".format(response.url))
        if self.is_index_page(url=response.url, response=response):
            self.process_index_page(response)
        elif self.is_captcha_page(response.url, response):
            self.process_captcha(response)
        elif self.is_results_page(response.url, response):
            items = self.process_question_answer_page(response)
            return items
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
        # posts = response.xpath(self.gt.css_to_xpath('.messageText')).extract()
        question_answer_list = []
        question_answer = QuestionAnswer()
        question_answer = self.fill_question(response, question_answer, question)

        # Cycle through posts and build Q/A pairs
        # posts = [BeautifulSoup(post).text.replace("\t", "").replace("\n", "").replace("\u00a0", "") for post in posts]
        posts = [post for post in posts[1:] if len(post) > 0]
        posts = self.filter_posts(response, posts)  # TODO implement function
        for answer_number in range(len(posts)):
            question_answer = self.fill_answer(response, question_answer, posts[answer_number])
            question_answer_list.append(question_answer)
        return question_answer_list

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


