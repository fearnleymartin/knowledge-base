import requests
import lxml.html
import lxml.etree as etree
from urllib.parse import urlparse
import os.path
from lxml.cssselect import CSSSelector
import datefinder
try:
    from .is_index_page import is_index_page, get_html, map_ex, get_leafs
except (SystemError, ImportError):
    from is_index_page import is_index_page, get_html, map_ex, get_leafs
import datetime
import queue
from copy import deepcopy
from datefinder import DateFinder
"""
We try to identify a results page contain question and answers
We use a structural approach
We try to detect a list of Q/A or forum posts
We look for a list of >= 2 posts, containing a date and user information
The block containing this list of posts is called the  lowest block
We try to make sure each post in the block has a minimum text length (avoid index pages and bad quality pages)
"""

# TODO: structure code into functions
# TODO speed up code, avoid going through whole tree, but perhaps flatten with regexes

min_text_len = 80
nodes_to_ignore = ['text/javascript']
url_blacklist = ['/blog/', '/topics/']
class_blacklist = []
text_tags = ['blockquote', 'article', 'p']


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def extract_dates(block):
    """
    Extract dates from raw html string
    We use a raw html string because date information is not necessarily contained in user visible text, but can also be
    contained in tag attributes
    :param block: lxml node
    :return: list of python date time objects
    """
    # TODO : important, have modified the source code of datefinder directly, should integrate this code into project code
    block_string = str(etree.tostring(block))
    # print(block_string)
    block_string = block_string.replace('Z', '')  # hacky
    matches = datefinder.find_dates(block_string, strict=True, source=True)
    # print(len(list(matches)))
    max_year = datetime.datetime.today().year
    min_year = 1970
    matches = [match[0] for match in matches if min_year <= match[0].year <= max_year and hasNumbers(match[1])]
    return matches


def contains_date(block):
    """
    :param block: lxml node
    :return: true if node contains date in html, false otherwise
    """
    # TODO improve strictness, is catching too many non dates
    # matches = extract_dates(block)
    # return len(list(matches)) > 0
    block_string = str(etree.tostring(block))
    block_string = block_string.replace('Z', '')  # hacky
    df = DateFinder()
    res = df.contains_date_strings(block_string, strict=True)
    return res


def contains_user(block):
    """
    For detecting the presence of user in html block
    Often css class contain the word user
    :param block: lxml node
    :return: true if node contains the word user in html
    """
    # TODO improve strictness, is too large still
    # TODO would like to restrict to tag information (ie classes, tag attributes with user in them
    block_string = str(etree.tostring(block))
    return 'user' in block_string or 'author' in block_string


def is_valid_block(block):
    """
    :param block: lxml node
    :return: true if block contains user and date information
    """
    # print(contains_date(block))
    # print(contains_user(block))
    return contains_date(block) and contains_user(block)


def get_text_leafs(html):
    """
    We want to extract all leaf nodes that contain text
    This is because usually text is located in leaf node
    :param html: lxml root node containing html
    :return: list of leaf nodes (lxml objects)
    """
    # TODO Try to find lowest common denominator (i.e. not paragraphs but an ensemble of paragraphs). Perhaps we can use beautiful soup ?
    leafs = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        children = node.getchildren()
        # Sometimes <br> tags are found in "leaf nodes" we skip these
        children = [child for child in children if child.tag != 'br']
        if node.tag in text_tags:
            leafs.append(node)
        if len(children) > 0:
            for child in children:
                stack.append(child)
        else:
            leafs.append(node)
    return leafs


def get_body(html):
    # TODO deal with empty list case
    body_list = list(filter(lambda child: child.tag == 'body', html.getchildren()))
    if len(body_list) > 0:
        return body_list[0]
    else:
        return None


def contains_min_text(html_node, min_text_len):
    """
    Checks one of the text leaf nodes contains at least min_text_len of text
    :param html_node:
    :param min_text_len:
    :return: true or false
    """
    # TODO sometimes problem is described by a picture
    min_text_len_bool = False
    leaves = get_text_leafs(html_node)

    for leaf in leaves:
        try:
            if len(leaf.text_content()) > min_text_len:
                min_text_len_bool = True
                break
        except ValueError:
            # sometimes get cyfunction ?
            # print('value error', leaf.tag, leaf.get('class'))
            pass
    return min_text_len_bool


def filter_by_css_classes(node):
    # TODO Implement faster way of checking all css classes
    css_classes = node.get('class')
    if css_classes:
        css_classes = css_classes.lower()
        css_classes = set(css_classes.split(' '))
        if len(css_classes) > 0:
            for blacklisted_class in class_blacklist:
                for css_class in css_classes:
                    if blacklisted_class == css_class:
                        print(css_class)
                        print('css class blacklisted', css_class)
                        return False
                    elif blacklisted_class + '_' in css_class or blacklisted_class + '-' in css_class:
                        print(css_class)
                        print('css class blacklisted', css_class)
                        return False
    return True

def filter_by_url(url):
    # TODO improve this with regexs
    # TODO overfitting at the moment
    for url_domain_clue in url_blacklist:
        if url_domain_clue in url: #  urlparse(url).netloc:
            print('url blacklisted')
            return True
    return False

def is_results_page(url, response=None):
    """
    :param url:
    :return: true if page is a results page, false otherwise
    We search for certain structure:
    A page must contain at least 2 valid blocks
    These are html nodes which contain a date and a user
    as is always the case for forum posts and Q/A sites
    """

    html = get_html(url, base_path='html_pages/results_{}.html', response=response)
    html = get_body(html)

    # Check url is not blacklisted
    if filter_by_url(url):
        return False


    # Check is not index page
    if is_index_page(url, input_html=deepcopy(html)):  # make sure not to modify html object
        print('false because index page')
        return False

    # change to BFS
    q = queue.Queue()
    q.put(html)

    res = False
    lowest_block = None
    while not q.empty():
        node = q.get()
        if node is None:
            continue
        # print(node)
        # print("curr_node", node.tag, node.get('class'))
        # Blacklist certain classes
        css_check = filter_by_css_classes(node)
        if css_check is False:
            return False

        child_blocks = node.getchildren()
        if len(child_blocks) > 0:

            valid_block_count = 0
            for child in child_blocks:

                if is_valid_block(child):
                    valid_block_count += 1

                    if child.get('type') not in nodes_to_ignore and child is not None:
                        q.put(child)  # a child can only be valid if parent is valid

            if valid_block_count >= 2:
                res = True
                if contains_min_text(node, min_text_len):
                    lowest_block = node
                    # print("lowest block:", lowest_block.tag, lowest_block.get('class'))



    # we check that lowest block contains min length of text
    if lowest_block is not None:
        pass
        print("final lowest block: ", lowest_block.tag, lowest_block.get('class'))
    else:
        print('no lowest block, returning false')
        return False

    # matches = extract_dates(lowest_block)
    # print(list(matches))

    min_text_len_bool = contains_min_text(lowest_block, min_text_len)

    if not min_text_len_bool:
        print('text body too short')


    return res and min_text_len_bool

if __name__ == "__main__":
    # index_page_url = 'https://redditblog.com/2017/03/02/rnintendoswitch-celebrates-switchmas-with-charity-live-stream/'
    # index_page_url = 'https://community.mindjet.com/mindjet/details'
    # index_page_url = 'http://www.dslreports.com/forum/r31291753-App-Update-MVPS-Host-File-Update-March-06-2017'
    # index_page_url = 'https://www.cnet.com/es/noticias/ghost-in-the-shell-scarlett-johansson-se-convierte-en-robot/'
    index_page_url = 'https://www.reddit.com/r/iphonehelp/comments/5z2o1r/two_problems_iphone_6_and_iphone_7/'
    # html = get_html(index_page_url)
    # print(etree.tostring(html))

    # print("date:", contains_date(block))
    # print("user:", contains_user(block))
    # print("valid block: ", is_valid_block(block))
    print(is_results_page(index_page_url))

