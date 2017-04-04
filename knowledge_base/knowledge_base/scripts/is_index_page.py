from urllib.parse import urlparse
import logging
try:
    from knowledge_base.knowledge_base.utils import get_html, process_html, extract_css_class
except:
    from knowledge_base.utils import get_html, process_html, extract_css_class
import sys
import lxml.etree as etree



class IsIndexPage(object):
    """
    The idea is to identify the structure of index pages
    Here we look for lists of at least 10 links on the same level of the html hierarchy
    We require one of the links to be a question at least
    """

    tag_blacklist = ['footer']
    indexPageLogger = logging.getLogger('indexPageLogger')

    def __init__(self):
        self.result_links = []
        # TODO implement pagination links
        self.pagination_links = []

    @staticmethod
    def map_ex(element_list):
        """
        For visualing elements
        :param element_list: list of elements
        :return: list of (tag, class) of elements
        """
        return list(map(lambda el: (el.tag, el.get('class')), element_list))


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



    def remove_leaves(self, html):
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
                            self.indexPageLogger.info('Attribute error')
                            self.indexPageLogger.info(node)
                            self.indexPageLogger.info(node.tag)
                            self.indexPageLogger.info(node.get('class'))
        return html


    def filter_links(self, html):
        """
        Remove non links leaves until only link tags are left in tree structure
        :param html:
        :return:
        """
        node_count = len(html.xpath(".//*"))
        new_node_count = 0
        while node_count != new_node_count:
            node_count = len(html.xpath(".//*"))
            html = self.remove_leaves(html)
            new_node_count = len(html.xpath(".//*"))
        return html


    def extract_nodes_with_over_x_children(self, html, num_children):
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
            if node.tag not in self.tag_blacklist:
                if len(node.getchildren()) > num_children:
                    nodes_list.append(node)
                if len(node.getchildren()) > 0:
                    for child in node.getchildren():
                        stack.append(child)
        return nodes_list


    def extract_links_from_subnodes(self, subnodes, index_page_url):
        """
        :param subnodes: list of lxml nodes
        :param index_page_url:
        :return: list of list of links
        The first list corresponds to the different subnodes, and the second one the links (lxml nodes) inside each subnode
        """
        res = []
        for subnode in subnodes:
            links = self.get_leafs(subnode)
            links = self.filter_links_list(links, index_page_url)
            if len(links) > 0:
                res.append(links)
        return res

    @staticmethod
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
            if link.get('href') is None or link.get('href') == "":
                val = False
            if val:
                res.append(link)
                # res_urls.add(urlparse(link.get('href')).path)
        res = list(set(res))
        return res


    def print_link_list(self, link_list):
        """
        Helper function for print the urls of link lxml object
        :param link_list: list of links (lxml object)
        :return:
        """
        for el in link_list:
            # print(el)
            # print(el.get('href'))
            self.indexPageLogger.info(el.get('href'))


    @staticmethod
    def identify_question(link):
        """
        :param link: lxml object
        :return: true if represents a question, false otherwise
        """
        # TODO to be improved !
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


    def subnode_is_index(self, subnode):
        """
        We consider a list to be a question list if it contains at least one question link
        :param subnode: list of links (lxml objects)
        :return:
        """
        for link in subnode:
            if self.identify_question(link):
                # print("question link", link.get('href'))
                return True
        return False


    def filter_subnode_links(self, subnode_links):
        """
        :param subnode_links: list of lxml node
        :return: list of lxml nodes which we believe show show have an index page
        """
        return [subnode for subnode in subnode_links if self.subnode_is_index(subnode)]


    def contains_pagination(self, html):
        """
        We want to check that the page contains a paginator
        For this we define a generic list of paginator class and verify that the page contains at least one
        :param html: lxml object
        :return: true if page contains paginator, false otherwise
        """

        # TODO improve with regexes
        pagination_classes = set(['pagination', 'pagenav', 'page-numbers', 'pager', 'next-button', 'nav-buttons'])
        css_classes = extract_css_class(str(etree.tostring(html)))
        for pagination_class in pagination_classes:
            if pagination_class in css_classes:
                self.indexPageLogger.info("pagination class: {}".format(pagination_class))
                return True
        return False

    def find_lists_of_links(self, html, index_page_url, list_len=9):
        """
        :param html:
        :param index_page_url:
        :param list_len:
        :return: list of list of links contained in html node
        """
        html = self.filter_links(html)  # Filter out all tags that aren't links (a)
        # print("html nodes links count: ", len(list(html.iter())))

        subnodes = self.extract_nodes_with_over_x_children(html, list_len)
        # print("subnodes count: ", len(subnodes))
        # print(map_ex(subnodes))
        subnode_links = self.extract_links_from_subnodes(subnodes, index_page_url)

        return subnode_links

    def is_index_page(self, index_page_url, response=None, input_html=None):
        """
        We need to have at least one node which is an index
        :param html: lxml html object
        :param index_page_url: the url of the page
        :return: true if is index page, false otherwise
        """
        # print('launch is index page for: {}'.format(index_page_url))
        # if response:
        #     # print('enter response of is index page')
        #     html = get_html(index_page_url, response=response)
        if input_html is not None:
            html = input_html
        else:
            # print('no response given')
            html = get_html(index_page_url, response=response)

        # TODO abstract out processing of html with making links absolute too
        html = process_html(html)

        if not self.contains_pagination(html):
            self.indexPageLogger.info('no pagination')
            # print('no pagination')
            return False

        lists_of_links = self.find_lists_of_links(html, index_page_url)

        # self.print_link_list(lists_of_links[3])

        index = self.filter_subnode_links(lists_of_links)
        if len(index) > 0:
            self.result_links = list(map(lambda x: x.get('href'), index[0]))
            self.indexPageLogger.info("extracted {} links from index page".format(len(index[0])))
        # print("is index page: ", len(index)>0)
        return len(index) > 0


if __name__ == "__main__":
    # index_page_url = 'https://forums.macrumors.com/threads/touch-id-problem-iphone-7.2034435/'
    # index_page_url = 'https://community.mindjet.com/mindjet/details'
    index_page_url = "http://stackoverflow.com/questions/tagged/regex"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    isIndexPage = IsIndexPage()
    print(isIndexPage.is_index_page(index_page_url))
    print(isIndexPage.result_links)
