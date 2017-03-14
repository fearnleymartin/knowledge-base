import requests
import lxml.html
import lxml.etree as etree
from urllib.parse import urlparse
import os.path

"""
The idea is to identify the structure of index pages
Here we look for lists of at least 10 links on the same level of the html hierarchy
We require one of the links to be a question at least
"""


def get_html(index_page_url, base_path='html_pages/{}.html' ):
    """
    If getting html page first time, we make a request and save the html to html_pages/<domain+path>.html
    Else we read html from file to save time
    :param index_page_url: the url of page to parse
    :return: lxml root node containing the page html
    """
    parsed_url = urlparse(index_page_url)
    scheme, domain, path = parsed_url.scheme, parsed_url.netloc, parsed_url.path
    base_href = scheme + '://' + domain
    path = base_path.format(domain+path.replace('/', '_'))

    if os.path.isfile(path):
        print('read_from_file')
        with open(path, encoding='utf-8') as html_file:
            index_page_html = html_file.read()
    else:
        # Changed the header because was getting blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(index_page_url, headers=headers)
        index_page_html = r.text
        with open(path, 'w', encoding='utf-8') as html_file:
            html_file.write(index_page_html)

    html = lxml.html.fromstring(index_page_html)
    html.make_links_absolute(base_href)
    return html


def map_ex(element_list):
    """
    For visualing elements
    :param element_list: list of elements
    :return: list of (tag, class) of elements
    """
    return list(map(lambda el: (el.tag, el.get('class')), element_list))


def get_leafs(html):
    """
    :param html: lxml root node containing html
    :return: list of leaf nodes (lxml objects)
    """
    leafs = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        children = node.getchildren()
        if len(children) > 0:
            for child in children:
                stack.append(child)
        else:
            leafs.append(node)
    return leafs


def remove_leaves(html):
    """
    :param html: lxml root node containing html
    :return: html with all leafs removed that aren't link (<a> tag)
    """
    leafs = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        children = node.getchildren()
        if len(children) > 0:
            for child in children:
                stack.append(child)
        else:
            leafs.append(node)
            if (node.tag != 'a') or (node.get('href') is None):
                if node.tag == 'html':
                    pass
                else:
                    try:
                        node.getparent().remove(node)
                    except AttributeError:
                        print('Attribute error')
                        print(node)
                        print(node.tag)
                        print(node.get('class'))
    return html


def filter_links(html):
    node_count = len(html.xpath(".//*"))
    new_node_count = 0
    while node_count != new_node_count:
        node_count = len(html.xpath(".//*"))
        html = remove_leaves(html)
        new_node_count = len(html.xpath(".//*"))
    return html


def extract_nodes_with_over_x_children(html, num_children):
    """
    :param html: lxml root node containing html
    :param num_children:
    :return: list of nodes that have over num_children children
    """
    nodes_list = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        if len(node.getchildren()) > num_children:
            nodes_list.append(node)
        if len(node.getchildren()) > 0:
            for child in node.getchildren():
                stack.append(child)
    return nodes_list


def extract_links_from_subnodes(subnodes, index_page_url):
    """
    :param subnodes: list of lxml nodes
    :param index_page_url:
    :return: list of list of links
    The first list corresponds to the different subnodes, and the second one the links (lxml nodes) inside each subnode
    """
    res = []
    for subnode in subnodes:
        links = get_leafs(subnode)
        links = filter_links_list(links, index_page_url)
        if len(links) > 0:
            res.append(links)
    return res


def filter_links_list(link_list, index_page_url):
    """
    :param link_list: list of links (lxml nodes)
    :param index_page_url:
    :return: the list with the following filtered out:
    blacklisted terms
    links which are notto the same domain
    remove duplicates
    """
    res = []
    # res_urls = set()
    blacklist = ['javascript:','mailto']
    for link in link_list:
        val = True
        for el in blacklist:  # for removing javascript links
            if el in link.get('href'):
                val = False
        if urlparse(index_page_url).netloc not in urlparse(link.get('href')).netloc and urlparse(link.get('href')).netloc not in urlparse(index_page_url).netloc:
            val = False
        # if urlparse(link.get('href')).path in res_urls:  # for removing duplicate links
        #     val = False
        if val:
            res.append(link)
            # res_urls.add(urlparse(link.get('href')).path)
    res = list(set(res))
    return res


def print_link_list(link_list):
    """
    Helper function for print the urls of link lxml object
    :param link_list: list of links (lxml object)
    :return:
    """
    for el in link_list:
        # print(el)
        print(el.get('href'))


def identify_question(link):
    """
    :param link: lxml object
    :return: true if represents a question, false otherwise
    """
    link_url = urlparse(link.get('href')).path
    link_text = link.text_content()

    question_words = ['how', 'when', 'where', 'what', 'who']
    problem_words = ['problem', 'issue', 'help']
    for el in question_words+problem_words:
        if (el + '_' in link_url) or (el + '-' in link_url):
            return True
        if el + ' ' in link_text:
            return True
    if '?' in link_url:
        return True
    if '?' in link_text:
        return True
    return False


def subnode_is_index(subnode):
    """
    We consider a list to be a question list if it contains at least one question link
    :param subnode: list of links (lxml objects)
    :return:
    """
    for link in subnode:
        if identify_question(link):
            # print(link.get('href'))
            return True
    return False


def filter_subnode_links(subnode_links):
    """
    :param subnode_links: list of lxml node
    :return: list of lxml nodes which we believe show show have an index page
    """
    return [subnode for subnode in subnode_links if subnode_is_index(subnode)]


def is_index_page(index_page_url):
    """
    We need to have at least one node which is an index
    :param html: lxml html object
    :param index_page_url: the url of the page
    :return: true if is index page, false otherwise
    """
    html = get_html(index_page_url)
    html = filter_links(html)
    subnodes = extract_nodes_with_over_x_children(html, 9)
    # print(map_ex(subnodes))
    subnode_links = extract_links_from_subnodes(subnodes, index_page_url)

    # print_link_list(subnode_links[0])

    index = filter_subnode_links(subnode_links)
    return len(index) > 0


if __name__ == "__main__":
    index_page_url = 'https://www.reddit.com/r/iphonehelp/comments/5z2o1r/two_problems_iphone_6_and_iphone_7/'
    print(is_index_page(index_page_url))
