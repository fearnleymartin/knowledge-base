from urllib.parse import urlparse
import logging
try:
    from knowledge_base.knowledge_base.utils import get_html, process_html, extract_css_class
except:
    from knowledge_base.utils import get_html, process_html, extract_css_class
import sys
import lxml.etree as etree
from lxml.cssselect import CSSSelector


class IsIndexPage(object):
    """
    This class contains functions to:
    - classify whether a page is an index page or not (is_index_page())
    - extract the links towards results pages and pagination links (contained in class attributes after running is_index_page())
    
    The idea is to detect lists of at least 10 links on the same level of the html hierarchy
    We require one of the links to be a question at least
    We also search for pagination elements.
    If we find both of these, then we classify the page as as index page
    
    N.B. Not used in latest version of crawler because not performing well enough
    """

    # Parameters
    tag_blacklist = ['footer']
    indexPageLogger = logging.getLogger('indexPageLogger')
    min_pagination_link_count = 1
    max_pagination_link_count = 12
    pagination_classes = ['pagination', 'pagenav', 'pager', 'page-numbers', 'next-button', 'nav-buttons', 'gotopage', 'pagenumber', 'paging']
    user_page_url_blacklist = ['/member/', '/members', '/user/', '/users/']
    url_blacklist = ['javascript:', 'mailto']

    def __init__(self, product=None):
        self.result_links = []
        self.pagination_links = []
        self.product = product
        self.is_pertinent = True

    @staticmethod
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

    def get_link_nodes_aux(self, html):
        """
        :param html: lxml root node containing html
        :return: html with all leafs removed that aren't links (<a> tag)
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
                            self.indexPageLogger.info('Attribute error')
                            self.indexPageLogger.info(node)
                            self.indexPageLogger.info(node.tag)
                            self.indexPageLogger.info(node.get('class'))
        return html

    def get_link_nodes(self, html):
        """
        The only elements that interest us in the html are the links.
        Therefore we filter out all other html elements from the html tree.
        To do this we recursively remove non-link leaves until only link tags are left in tree structure
        :param html: lxml node
        :return: lxml node where the tree it contains contains only link nodes
        """
        node_count = len(html.xpath(".//*"))
        new_node_count = 0
        while node_count != new_node_count:
            node_count = len(html.xpath(".//*"))
            html = self.get_link_nodes_aux(html)
            new_node_count = len(html.xpath(".//*"))
        return html

    def extract_nodes_with_over_x_children(self, html, num_children):
        """
        We search for nodes that have over a certain amount of children. These are potential
        containers of the list of links we are searching for..
        :param html: lxml root node containing html
        :param num_children:
        :return: list of nodes that have over num_children children
        """
        nodes_list = []
        stack = []
        stack.append(html)
        while len(stack) > 0:
            node = stack.pop()
            if node.tag not in self.tag_blacklist:
                if len(node.getchildren()) > num_children:
                    nodes_list.append(node)
                if len(node.getchildren()) > 0:
                    for child in node.getchildren():
                        stack.append(child)
        return nodes_list

    def extract_links_from_subnodes(self, subnodes, index_page_url):
        """
        Given the potential containers of the list of index links, we want to extract a list of links contained ineach container
        :param subnodes: list of lxml nodes
        :param index_page_url:
        :return: list of list of links
        The outer list corresponds to the different subnodes, and the inner lists correspond to the links (lxml nodes) inside each subnode
        """
        res = []
        for subnode in subnodes:
            links = self.get_leafs(subnode)
            links = self.filter_links_list(links, index_page_url)
            if len(links) > 0:
                res.append(links)
        return res

    def filter_links_list(self, link_list, index_page_url):
        """
        :param link_list: list of links (lxml nodes)
        :param index_page_url:
        :return: the list with the following filtered out:
        blacklisted terms
        links which are not to the same domain
        remove duplicates
        """
        res = []
        blacklist = self.url_blacklist + self.user_page_url_blacklist
        for link in link_list:
            val = True
            for el in blacklist:  # for removing javascript links
                if el in link.get('href'):
                    val = False
            if urlparse(index_page_url).netloc not in urlparse(link.get('href')).netloc and urlparse(link.get('href')).netloc not in urlparse(index_page_url).netloc:
                val = False
            if link.get('href') is None or link.get('href') == "":
                val = False
            if val:
                res.append(link)
        res = list(set(res))
        return res

    @staticmethod
    def identify_question(link):
        """
        :param link: lxml object
        :return: true if represents a question, false otherwise
        """
        # TODO very simplistic detection, can be improved
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

    def is_index_list(self, list_of_links):
        """
        We consider a list to be a question list if it contains at least one question link
        :param list_of_links: list of links (lxml objects)
        :return:
        """
        for link in list_of_links:
            if self.identify_question(link):
                return True
        return False

    def filter_index_lists(self, subnode_links):
        """
        :param subnode_links: list of lxml nodes that contains lists of links
        :return: list of lxml nodes which we believe should have an index page
        """
        return [subnode for subnode in subnode_links if self.is_index_list(subnode)]

    def remove_user_page_links(self, link_list):
        """
        :param link_list: 
        :return: the link_list with all links towards member profile pages removed
        """
        filtered_link_list = []
        for link in link_list:
            if '/user/' not in link and '/member/' not in link:
                filtered_link_list.append(link)
        return filtered_link_list

    def contains_pagination(self, html):
        """
        We want to check that the page contains a paginator
        For this we define a generic list of paginator classes and verify that the page contains at least one
        :param html: lxml object
        :return: true if page contains paginator, false otherwise
        """
        css_classes = extract_css_class(str(etree.tostring(html))).split(' ')
        css_classes_lower = list(map(lambda x: x.lower(), css_classes))
        for pagination_class in self.pagination_classes:
            for css_class_lower in css_classes_lower:
                if pagination_class in css_class_lower:
                    _pagination_class = css_classes[css_classes_lower.index(css_class_lower)]  # To get version with capitalisations

                    # strategy: find lowest node with at least 5 links. Take this one as parent pagination node
                    # might be some noise but doesn't really matter
                    self.indexPageLogger.info("pagination class: {}".format(_pagination_class))

                    sel = CSSSelector(".{}".format(_pagination_class))
                    if len(sel(html)) > 0:
                        pagination_node = list(sel(html))[0]
                        link_count = len(self.remove_user_page_links(list(pagination_node.iterlinks())))
                        max_iters = 20
                        iter_count = 0
                        while link_count < self.min_pagination_link_count and iter_count < max_iters:
                            parent_pagination_node = pagination_node.getparent()
                            link_count = len(self.remove_user_page_links(list(parent_pagination_node.iterlinks())))
                            if link_count > self.max_pagination_link_count:
                                pagination_node = parent_pagination_node
                            iter_count += 1
                        if iter_count == max_iters:
                            self.indexPageLogger.info('not enough links or too many links in pagination')
                            return False
                        self.indexPageLogger.info("final pagination class: {}, {}".format(pagination_node.get('class'), pagination_node.get('id')))
                        # TODO filter links (ex: no pngs)
                        self.pagination_links = list(filter(lambda x: x is not None, map(lambda x:  x[2] if len(x) >= 2 else None, self.remove_user_page_links(pagination_node.iterlinks()))))
                        self.indexPageLogger.info("extracted {} paginationlinks".format(len(self.pagination_links)))
                    else:
                        return False

                    return True

        return False

    def links_contains_product(self, link_text):
        """
        Check a block contains the product keyword
        :param text_content: the text content of a block
        :return: True if the link text contains the product, False otherwise
        """
        product_words = self.product.split(' ')
        product_bool = False
        for product_word in product_words:
            if product_word.lower() in link_text.lower():
                product_bool = True
        return product_bool

    def find_lists_of_links(self, html, index_page_url, list_len=9):
        """
        :param html:
        :param index_page_url:
        :param list_len:
        :return: list of list of links contained in html node
        """
        html = self.get_link_nodes(html)  # Filter out all tags that aren't links (a)
        subnodes = self.extract_nodes_with_over_x_children(html, list_len)
        subnode_links = self.extract_links_from_subnodes(subnodes, index_page_url)

        return subnode_links

    def is_index_page(self, index_page_url, response=None, input_html=None):
        """
        We need to have at least one node which is an index
        :param html: lxml html object
        :param index_page_url: the url of the page
        :return: true if is index page, false otherwise
        """

        self.is_pertinent = True

        if input_html is not None:
            html = input_html
        else:
            html = get_html(index_page_url, response=response)

        html = process_html(html)
        if html is None:
            return False

        if not self.contains_pagination(html):
            self.indexPageLogger.info('no pagination')
            return False

        lists_of_links = self.find_lists_of_links(html, index_page_url)

        index = self.filter_index_lists(lists_of_links)
        if len(index) > 0:
            if self.product:  # filter out non pertinent links (i.e. not related to product)
                product_count = 0
                for link in index[0]:
                    print(link.text_content())
                    if self.links_contains_product(link.text_content()) or self.links_contains_product(link.get('href')):
                        product_count += 1
                if product_count == 0:
                    self.is_pertinent = False
            self.result_links = list(map(lambda x: x.get('href'), index[0]))
            self.indexPageLogger.info("extracted {} links from index page".format(len(index[0])))
        # print("is index page: ", len(index)>0)
        return len(index) > 0


if __name__ == "__main__":
    # For testing the algorithm
    index_page_url = "http://stackoverflow.com/questions/tagged/iphone"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    isIndexPage = IsIndexPage(product="iphone")
    print(isIndexPage.is_index_page(index_page_url))
    print('----------------------------------------')
    print(isIndexPage.result_links)
    print('-----------------------------------------')
    print(isIndexPage.pagination_links)
