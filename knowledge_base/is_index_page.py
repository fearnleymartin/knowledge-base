import requests
import lxml.html
import lxml.etree as etree
from urllib.parse import urlparse
import os.path

# index_page_url = 'https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/'

#
# with open('reddit_index_page_html.html', 'w', encoding='utf-8') as html_file:
#     html_file.write(index_page_html)


# with open('reddit_index_page_html.html', encoding='utf-8') as html_file:
#     index_page_html = html_file.read()


def get_html(index_page_url):
    base_href = urlparse(index_page_url).scheme + '://' + urlparse(index_page_url).netloc
    path = 'html_pages/{}.html'.format(urlparse(index_page_url).netloc+urlparse(index_page_url).path.replace('/','_'))
    if os.path.isfile(path):
        # print('read_from_file')
        with open(path, encoding='utf-8') as html_file:
            index_page_html = html_file.read()
    else:
        r = requests.get(index_page_url)
        index_page_html = r.text
        with open(path, 'w', encoding='utf-8') as html_file:
            html_file.write(index_page_html)


    html = lxml.html.fromstring(index_page_html)
    html.make_links_absolute(base_href)
    return html

# links = list(html.iterlinks())
#
# links_hier_dict = {}

def get_hierarchy_list(link_el):
    hierarchy_list = []
    while link_el.getparent() is not None:
        hierarchy_list.append(link_el.getparent())
        link_el = link_el.getparent()
    return hierarchy_list

# for link in links:
#     links_hier_dict[link] = get_hierarchy_list(link[0])

# get('class')

# l=links_hier_dict[links[194]]

# h = []
# for i in range(len(l)):
#     h.append((l[i].tag,l[i].get('class')))

def map_ex(l):
    return list(map(lambda el: (el.tag, el.get('class')),l))

def get_leafs(html):
    leafs = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        # print(node)
        if len(node.getchildren()) > 0:
            for child in node.getchildren():
                stack.append(child)
        else:
            leafs.append(node)
            # if node.tag != 'a':
            #     node.getparent().remove(node)
    return leafs


def remove_leafs(html):
    leafs = []
    stack = []
    stack.append(html)
    while len(stack) > 0:
        node = stack.pop()
        # print(node)
        if len(node.getchildren()) > 0:
            for child in node.getchildren():
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
        html = remove_leafs(html)
        new_node_count = len(html.xpath(".//*"))
    return html


def extract_nodes_with_over_x_children(tree, num_children):
    nodes_list = []
    stack = []
    stack.append(tree)
    while len(stack) > 0:
        node = stack.pop()
        # if node.tag == 'ol':
        #     print(node.tag, node.get('class'))
        if len(node.getchildren()) > num_children:
            nodes_list.append(node)
        if len(node.getchildren()) > 0:
            for child in node.getchildren():
                stack.append(child)
    return nodes_list

def extract_links_from_subnodes(subnodes, index_page_url):
    res = []
    for subnode in subnodes:
        links = get_leafs(subnode)
        links = filter_links_list(links, index_page_url)
        if len(links) > 0:
            res.append(links)
    return res

def filter_links_list(link_list, index_page_url):
    res = []
    # res_urls = set()
    noise = ['javascript:','mailto']
    for link in link_list:
        val = True
        for el in noise:  # for removing javascript links
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
    for el in link_list:
        # print(el)
        print(el.get('href'))

def identify_question(link):
    link_url = urlparse(link.get('href')).path
    link_text = link.text_content()
    # if 'thread' in link_url:
    #     print(etree.tostring(link))
    # print(link_url)
    # print(link_text)
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
    for link in subnode:
        if identify_question(link):
            print(link.get('href'))
            return True
    return False

def filter_subnode_links(subnode_links):
    return [subnode for subnode in subnode_links if subnode_is_index(subnode)]

def is_index_page(html, index_page_url):
    html = filter_links(html)
    leafs = get_leafs(html)

    subnodes = extract_nodes_with_over_x_children(html, 9)
    print(map_ex(subnodes))
    subnode_links = extract_links_from_subnodes(subnodes, index_page_url)
    # print('start')
    # print(len(subnode_links[0]))
    # print_link_list(subnode_links[2])
    # print('end')
    # print(subnode_links)
    index = filter_subnode_links(subnode_links)
    print(len(index))
    # print(index)
    # print(index)
    return len(index) > 0

if __name__ == "__main__":
    # index_page_url = 'https://www.reddit.com/r/iphonehelp/'
    index_page_url = 'http://forums.macrumors.com'
    # base_href = urlparse(index_page_url).scheme + '://' + urlparse(index_page_url).netloc
    #
    # r = requests.get(index_page_url)
    # index_page_html = r.text
    #
    # html = lxml.html.fromstring(index_page_html)
    # html.make_links_absolute(base_href)
    html = get_html(index_page_url)
    print(is_index_page(html, index_page_url))

# html = filter_links(html)
# leafs = get_leafs(html)
# subnodes = extract_nodes_with_over_x_children(html, 9)
# print(subnodes)
# subnode_links = extract_links_from_subnodes(subnodes)
# index = filter_subnode_links(subnode_links)

# print_link_list(subnode_links[0])
# print(len(index))

# string = lxml.html.tostring(html, pretty_print=True)

# with open('filteredhtml.html', 'wb') as html_file:
#     html_file.write(string)
# html.write('filteredhtml.html')

# print(string)

