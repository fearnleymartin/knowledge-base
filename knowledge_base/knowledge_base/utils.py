from urllib.parse import urlparse
import lxml.html
import requests
import logging
from lxml.html.clean import Cleaner
import os
import re

utils_logger = logging.getLogger('utils_logger')
cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


def date_to_solr_format(datetime_object):
    """
    http://lucene.apache.org/solr/4_4_0/solr-core/org/apache/solr/schema/DateField.html
    :param datetime_object:
    :return: datetime as string in solr format. Ex: 1995-12-31T23:59:59Z
    """
    return datetime_object.isoformat()


def get_body(html):
    """
    :param html: 
    :return: body node of hmtl
    """
    body_list = list(filter(lambda child: child.tag == 'body', html.getchildren()))
    if len(body_list) > 0:
        return body_list[0]
    else:
        return None


def get_html(page_url, base_path='html_pages/{}.html', response=None):
    """
    If getting html page first time, we make a request and save the html to html_pages/<domain+path>.html
    Else we read html from file to save time
    :param page_url: the url of page to parse
    :return: lxml root node containing the page html
    """
    parsed_url = urlparse(page_url)
    scheme, domain, path = parsed_url.scheme, parsed_url.netloc, parsed_url.path
    base_href = scheme + '://' + domain
    base_dir_path = 'c:/Users/fearnley/Documents/swisscom/knowledge-base/knowledge_base/'
    path = base_dir_path+base_path.format(domain+path.replace('/', '_'))

    html = None
    if response:
        utils_logger.info('read from response')
        index_page_html = response.body
    else:
        if os.path.isfile(path):
            print('read_from_file')
            utils_logger.info('read_from_file: {}'.format(path))
            print(path)
            with open(path, encoding='utf-8') as html_file:
                    index_page_html = html_file.read()
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            r = requests.get(page_url, headers=headers)
            index_page_html = r.text
            with open(path, 'w', encoding='utf-8') as html_file:
                html_file.write(index_page_html)
            utils_logger.info('write to file')

    html = lxml.html.fromstring(index_page_html)
    html.make_links_absolute(base_href)
    return html


def process_html(html):
    """
    :param html: 
    :return: cleaned body node of html
    """
    html = get_body(html)
    if html is None:
        utils_logger.info('no body')

    html = cleaner.clean_html(html)
    if html is None:
        utils_logger.info('only js')
    return html

def extract_css_class(string):
    """
    :param string: html in string format
    :return: a string of the css classes separated by a space
    """
    pattern = r"class=\"+[^\"\r\n]*"
    return " ".join(list(map(lambda x: x.replace('class=', "").replace("\"", ''), re.findall(pattern, string))))


def url_to_short_file_name(url):
    """
    :param url: 
    :return: shortened url to use in file names
    """
    return url.replace('https://', '').replace('http://', '').replace('/', '_').replace('=', '').replace('?','')[:100]


def format_html_node_for_print(node, text):
    """
    
    :param node: lxml node
    :param text: text to display
    :return: human readable version of lxml node for debugging purposes
    """
    return '{}: {}, {}, {}'.format(text, node.tag, node.get('class'),node.get('id'))