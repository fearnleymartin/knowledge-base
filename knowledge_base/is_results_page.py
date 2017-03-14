import requests
import lxml.html
import lxml.etree as etree
from urllib.parse import urlparse
import os.path
from lxml.cssselect import CSSSelector
import datefinder
from is_index_page import is_index_page, get_html


def contains_date(block):
    """
    :param block: lxml node
    :return: true if node contains date in html, false otherwise
    """
    block_string = str(etree.tostring(block))
    matches = datefinder.find_dates(block_string)
    return len(list(matches)) > 0


def contains_user(block):
    """
    For detecting the presence of user in html block
    Often css class contain the word user
    :param block: lxml node
    :return: true if node contains the word user in html
    """
    block_string = str(etree.tostring(block))
    return 'user' in block_string


def is_valid_block(block):
    """
    :param block: lxml node
    :return: true if block contains user and date information
    """
    return contains_date(block) and contains_user(block)


def is_results_page(url):
    """
    :param url:
    :return: true if page is a results page, false otherwise
    We search for certain structure:
    A page must contain at least 2 valid blocks
    These are html nodes which contain a date and a user
    as is always the case for forum posts and Q/A sites
    """
    # TODO: Find lowest common denominator of blocks
    # TODO: Make sure blocks contain text of a minimum length
    html = get_html(url, base_path='html_pages/results_{}.html')

    url_blacklist = ['blog']
    for url_domain_clue in url_blacklist:
        if url_domain_clue in urlparse(url).netloc:
            return False

    if is_index_page(html, url):
        print('false because index page')
        return False

    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        child_blocks = node.getchildren()
        if len(child_blocks) > 0:
            valid_block_count = 0
            for child in child_blocks:
                if is_valid_block(child):
                    valid_block_count += 1
                stack.append(child)
            if valid_block_count >= 2:
                print(node.tag, node.get('class'))
                return True
    return False

if __name__ == "__main__":
    index_page_url = 'https://redditblog.com/2017/03/02/rnintendoswitch-celebrates-switchmas-with-charity-live-stream/'

    # sel = CSSSelector('.post-signature.owner')
    # block = sel(html)[0]
    # print("date:", contains_date(block))
    # print("user:", contains_user(block))
    # print("valid block: ", is_valid_block(block))
    print(is_results_page(index_page_url))

