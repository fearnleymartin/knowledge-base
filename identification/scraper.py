# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 11:07:20 2015
Contains the scripts for the ranktracker
@author: Fearnley Martin


ERROR CODES:
100: not ranked
0: connection error


Example of use :
s=Scraper()
d = {'parsed_keyword' : 'test', 'domain':'google.fr','lang_code':'fr'}
s.get_google_result_urls_for_keyword( None, **d) #return a boolean
print(s.google_result_urls)

"""
from lxml import html
import datetime
import requests
from bs4 import BeautifulSoup
import re
import tldextract



class Scraper(object):
    """
    Class for scraping google and getting rankings for individual keyword
    Use method find rank for this
    get_google_result_urls_for_keyword scrapes google serp page and gets lit of result urls
    """

    def __init__(self, last_result=100):
        """
        :param last_result: The number of SERP results checked
        :return:
        """
        self.lastResult = last_result
        # EMPIRICAL RULE : Each url containing the first_mark pattern,
        # immediately followed by an url that contains the second_mark pattern,
        # contains the url we want to get.
        self.first_mark = "/url?q="
        self.second_mark = '/url?q=http://webcache.googleusercontent.com/search'
        self.latin = [u' ', u'!', u'"', u'#', u'$', u'%', u'&', u'\'', u'(', u')', u'*', u'+', u',', u'-', u'.', u'/',
                      u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u':', u';',
                      u'<', u'=', u'>', u'?', u'@', u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K',
                      u'L', u'M', u'N',
                      u'O', u'P',
                      u'Q', u'R', u'S',
                      u'T', u'U', u'V', u'W', u'X', u'Y', u'Z', u'[', u'\\', u']', u'^', u'_', u'`',
                      u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p',
                      u'q', u'r',
                      u's', u't', u'u', u'v', u'w', u'x', u'y', u'z', u'{', u'|', u'}', u'~',
                      u'¡', u'¢', u'£', u'¤', u'¥', u'¦', u'§', u'¨', u'©', u'ª', u'«', u'¬', u'®', u'¯', u'°', u'±',
                      u'²', u'³',
                      u'´', u'µ', u'¶', u'·', u'¸', u'¹', u'º', u'»', u'¼', u'½', u'¾', u'¿', u'À', u'Á', u'Â', u'Ã',
                      u'Ä', u'Å',
                      u'Æ', u'Ç', u'È', u'É', u'Ê', u'Ë', u'Ì', u'Í', u'Î', u'Ï', u'Ð', u'Ñ', u'Ò', u'Ó', u'Ô', u'Õ',
                      u'Ö', u'×',
                      u'Ø', u'Ù', u'Ú', u'Û', u'Ü', u'Ý', u'Þ', u'ß', u'à', u'á', u'â', u'ã', u'ä', u'å', u'æ', u'ç',
                      u'è', u'é',
                      u'ê', u'ë', u'ì', u'í', u'î', u'ï', u'ð', u'ñ', u'ò', u'ó', u'ô', u'õ', u'ö', u'÷', u'ø', u'ù',
                      u'ú', u'û',
                      u'ü', u'ý', u'þ', u'ÿ'
                      ]
        # basic latin + latin 1 supplement
        self.all_accepted_symbols = self.latin
        self.characters_to_encode = [u'!', u'#', u'$', u'&', u'\'', u'(', u')', u'+', u',', u'/', u':', u';',
                                     u'=', u'?', u'@', u'[', u'\\', u']', u'^', u'`', u'{', u'|', u'}', u'"']
        self.google_result_urls = []  # List of urls scrapped from google serp page

    @staticmethod
    def link_parser(link):
        """
        Treats the links from google to extract urls
        Much easier to take the links from the url beginning with "/url?q="
        :param link: the link to be parsed (the part you want is contained between "/url?q=" and "&sa"
        :return: the link you need
        >>> s = Scraper()
        >>> link = "/url?q=http://www.lepointdufle.net/tests-de-francais.htm&sa=U&ved=0ahUKEwi4jv-IwrnNAhVnKsAKHWh-BO8QFgjjBDBj&usg=AFQjCNErIS4pGpLqP6YM6RrQy-B4U77t8w"
        >>> s.link_parser(link)
        >>> 'http://www.lepointdufle.net/tests-de-francais.htm'
        """
        start_mark = "/url?q="
        end_mark = "&sa"
        return link[len(start_mark):link.find(end_mark)]

    def get_google_html_code(self, url):
        """
        Essentially checked html sent back from google is in parsable format
        @param url: a url for a google search ex: 'http://google.fr/search?q=test&hl=fr&pws=0&as_qdr=all&gl=fr&num=50'
        @return: gets the html code of a page and returns as lxml.html object
        """
        session = requests.Session()
        request = session.get('https://www.google.com/ncr')
        request = session.get(url)
        html_code = request.text
        if request.status_code != 200:  # Check server returns response
            raise requests.ConnectionError('Connection failed')
        elif self.second_mark not in html_code:  # Check response is in correct format
            # The format required for getting links always contains second mark
            # Otherwise the request has failed, or google has changed their output
            raise requests.ConnectionError('Request blocked')
        else:
            return html_code

    @staticmethod
    def get_links_from_html(html_code):
        """ Takes the html code and parses with lxml to return links
        @param html_code: html to be passed for links
        @return: lxml iterlinks object
        >>> s=Scraper()
        >>> html_code = "<body><h1>Not a link</h1><a href=\"testlink.com\">A real link</a></body>"
        >>> s.get_links_from_html(html_code)
        >>> <generator object iterlinks at 0x000000000316ECA8>
        """
        return html.fromstring(html_code).iterlinks()


    def filter_lxml_google_links_to_serp_results_list(self, links):
        """

        @param links: lxml links object from google html
        @return: list of links parsed so that contains only results links
        """
        results = []
        # format standard d'une recherche google
        links = [link for link in links]  # Not really exploiting iterators
        for k in range(0, len(links)):  # iterateur sur les liens de la page... GENIAL
            if k < len(links) - 1:
                link = links[k][2]  # get the link url from link object(link is a 4-tuple)
                next_link = links[k + 1][2]  # Links come by two and we only want the first
                if self.first_mark in link and self.second_mark not in link and self.second_mark in next_link:
                    parsed_link = self.link_parser(link)
                    results.append(parsed_link)
        return results

    def get_google_result_urls_for_keyword(self, **kwargs):
        """
        gets list of the urls found when typing keyword into google
        :param keyword: keyword object corresponding to a google request
        :return: True if request succeeds, False otherwise
        >>> s=Scraper()
        >>> s.get_google_result_urls_for_keyword('test', 'google.fr','fr')
        ['https://www.16personalities.com/fr/test-de-personnalite',
        'http://test-orientation.studyrama.com/choixType.php',
        'http://test.psychologies.com/',
        'http://www.speedtest.net/fr/',
        'http://www.mon-qi.com/test-memoire/test.php',
        'http://www.mon-qi.com/tests-de-qi.php',
        ...
        ]
        for localisation see: https://moz.com/ugc/geolocation-the-ultimate-tip-to-emulate-local-search
        search_engine: 'google.fr' or 'google.com' for example
        lang_code: 'fr' or 'en' for example
        location: optional parameter for specifying location
        """

        parsed_keyword = kwargs['parsed_keyword']
        search_engine = kwargs['domain']
        lang_code = kwargs['lang_code']
        location = None


        url = "https://www.%s/search?q=%s&hl=%s&pws=0&as_qdr=all&gl=%s&num=%s" % (
            search_engine,  # ex google.com
            parsed_keyword,  # &q=
            lang_code,  # &hl=
            lang_code,  # & gl= (country_code)
            str(self.lastResult)  # number of results
        )
        # print(location)
        if location:
            location_string = "&tci=g:%s&uule=w+CAIQICI%s%s" % (
                location.id_location,  # tci=g: location id
                location.secret_key,  # secret key for location
                location.canonical_name_base_64  # base 64 encoded location ame
            )
            url += location_string
        # pws: personalised search
        # as_qdr: how long ago results were indexed
        try:
            links = Scraper.get_links_from_html(self.get_google_html_code(url))
            self.google_result_urls = self.filter_lxml_google_links_to_serp_results_list(links)
            return True
        except requests.ConnectionError:
            return False

