import lxml.etree as etree
import lxml.html
import datefinder
import datetime
import queue
from copy import deepcopy
from lxml.html.clean import Cleaner
import logging
import sys
import re
from lxml.cssselect import CSSSelector
from urllib.parse import urlparse
try:  # scrapy giving import problems
    from knowledge_base.knowledge_base.scripts.is_index_page import IsIndexPage
    from knowledge_base.knowledge_base.scripts.datefinder import DateFinder
    from knowledge_base.knowledge_base.utils import extract_css_class, get_html, format_html_node_for_print
except (SystemError, ImportError):
    from knowledge_base.scripts.is_index_page import IsIndexPage
    from knowledge_base.scripts.datefinder import DateFinder
    from knowledge_base.utils import extract_css_class, get_html, format_html_node_for_print


"""
The method `is_results_page`: identifies a results page containing question and answers (from the url): True or False
The class stores the questions and answers in the list `parsed_text_content`
This list contains dictionaries of the form {'date' : '...', 'author': '...', 'author_link': '...', 'body': '...'}

We use a structural approach
We try to detect a list of Q/A or forum posts
We look for a list of >= 2 posts, containing a date and user information
The block containing this list of posts is called the  lowest block
We try to make sure each post in the block has a minimum text length (avoid index pages and bad quality pages)
"""

class IsResultsPage(object):

    logger = logging.getLogger('isResultsPage')

    # params
    min_text_len = 150
    max_text_len = 5000
    nodes_to_ignore = ['text/javascript']
    url_blacklist = ['/blog/']
    class_blacklist = []
    tag_blacklist = ['footer']
    text_tags = ['blockquote', 'article', 'p']
    child_tag_blacklist = ['script']
    input_node_type_blacklist = ['password', 'username']  # input nodes types which cause us to declare a block non valid
    input_node_placeholder_blacklist = ['search']  # input node placeholders which cause us to declare a block non valid
    block_max_links = 8  # filter out blocks with more than 8 links (filter out menus etc)

    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True
    cleaner.forms = False

    def __init__(self, product=None):
        self.url = None  # url of page to analyse
        self.text_content = []  # contains the non-parsed posts
        self.parsed_text_content = []  # contains the parsed posts
        self.valid_blocks = []  # contains the non parsed posts
        self.isIndexPage = IsIndexPage()
        self.reason = ''  # Why the page was classified as results or not
        self.product = product  # Product to filter by, will only keep pages that contain the product text
        self.html = None
        self.is_pertinent = True

    @staticmethod
    def hasNumbers(inputString):
        """
        Checks if a string contains numbers
        :param inputString: 
        :return: True if inputString contains numbers, False otherwise
        """
        return any(char.isdigit() for char in inputString)

    def set_reason(self, reason):
        """
        Helper function to print log reason for classification
        :param reason: 
        :return: 
        """
        self.reason = reason
        self.logger.info(reason)

    def extract_dates(self, block, string=None):
        """
        Extract dates from raw html string
        We use a raw html string because date information is not necessarily contained in user visible text, but can also be contained in tag attributes
        :param block: lxml node
        :return: list of python date time objects
        """
        if string:
            block_string = string
        else:
            block_string = str(etree.tostring(block))
        block_string = block_string.replace('Z', '')  # hacky
        matches = datefinder.find_dates(block_string, strict=True, source=True)
        max_year = datetime.datetime.today().year
        min_year = 1970
        matches = [(match[0],match[1]) for match in matches if min_year <= match[0].year <= max_year and self.hasNumbers(match[1])]
        return matches

    @staticmethod
    def contains_date(block):
        """
        :param block: lxml node
        :return: true if node contains date in html, false otherwise
        """
        block_string = str(etree.tostring(block))
        pattern = r'<(a|/a).*?>'
        block_string = re.sub(pattern, "", block_string)
        block_string = block_string.replace('Z', '')  # hacky
        df = DateFinder()
        res = df.contains_date_strings(block_string, strict=True)
        return res

    def extract_user_node(self, block):
        """
        Step 1: Look for all css classes corresponding to possible user blocks
        Step 2: Find valid user nodes out of possible nodes (needs to contain link to user profile)
        Step 3: Once valid block identified, extract and return corresponding information
        :param block: lxml node corresponding to a block
        :return: a tuple containing:
        - the lxml node corresponding the user block inside the input block
        - the corresponding user css class
        - the link to the user's profile
        - the text inside the user block (usually the user name)
        """
        block_copy = deepcopy(block)
        block_string = str(etree.tostring(block_copy))
        # Step 1
        css_classes_list = extract_css_class(block_string).split(' ')
        user_css_class = None
        user_css_classes = []
        for css_class in css_classes_list:
            if 'user' in css_class or 'author' in css_class:
                user_css_classes.append(css_class)

        if len(user_css_classes) > 0:

            # Step 2
            # There could be possible user_nodes, we only take the one the satisfies extra criteria
            user_nodes = []
            for user_css_class in user_css_classes:
                user_nodes += list(CSSSelector('.{}'.format(user_css_class))(block_copy))
            valid_user_nodes = []  # list of tuples containing (user node, list of links in user node)
            for _user_node in user_nodes:
                links = _user_node.iterlinks()
                filtered_links = []
                # Filter links 1) on site 2) a tags 3) duplicates 4) text content not null 5) contains no dates
                # Idea is when a user is mentioned, there is always a link to his profile
                for link in links:
                    if link[0].tag == 'a':
                        if urlparse(link[2]).netloc == urlparse(self.url).netloc:
                            if link[1] not in [link[1] for link in filtered_links]:
                                if len(self.extract_text_content(link[0])) > 0:
                                    if not self.contains_date(link[0]):
                                        filtered_links.append(link)
                if len(filtered_links) > 0:
                    valid_user_nodes.append((_user_node, filtered_links))
                    break

            # Step 3
            if len(valid_user_nodes) == 0:
                user_node = None
                user_link = None
                user_text = None
            else:  # No valid user nodes
                user_node_pair = valid_user_nodes[0]  # Take the first node
                user_node = user_node_pair[0]
                filtered_links = user_node_pair[1]
                if len(filtered_links) > 1:
                    self.logger.debug('multiple user  links found')
                user_link = filtered_links[0][2]
                user_text = self.extract_text_content(filtered_links[0][0])
        else:  # No valid user nodes
            user_node = None
            user_link = None
            user_text = None
        return user_node, user_css_class, user_link, user_text

    def contains_user(self, block):
        """
        For detecting the presence of user in html block
        Often css class contain the word user
        :param block: lxml node
        :return: true if node contains the word user in html
        """
        user_node = self.extract_user_node(block)[0]
        return user_node is not None

    def is_valid_block(self, block):
        """
        :param block: lxml node
        :return: true if block contains user and date information
        """
        text = self.extract_text_content(block)
        return self.contains_date(block) and self.contains_user(block) and self.is_over_min_text_len(text, self.min_text_len)

    def filter_valid_blocks(self, block):
        """
        We black list certain things we don't want to find in blocks
        Search bar, login etc
        :param block: 
        :return: 
        """
        block_string = lxml.html.fromstring(lxml.html.tostring(block))
        input_nodes = block_string.xpath('//input')
        input_nodes = [i for i in input_nodes if i.get('type') != 'hidden' and (i.get('type') in self.input_node_type_blacklist or i.get('placeholder') in self.input_node_placeholder_blacklist)]
        doesnt_contain_input_nodes = len(input_nodes) == 0
        return doesnt_contain_input_nodes

    @staticmethod
    def get_body(html):
        """
        :param html: 
        :return: body node of the html
        """
        body_list = list(filter(lambda child: child.tag == 'body', html.getchildren()))
        if len(body_list) > 0:
            return body_list[0]
        else:
            return None

    @staticmethod
    def is_over_min_text_len(text, min_text_len):
        """
        Checks one of the text leaf nodes contains at least min_text_len of text
        :param text:
        :param min_text_len:
        :return: true or false
        """
        return len(text) > min_text_len

    @staticmethod
    def is_under_max_text_len(text, max_text_len):
        return len(text) < max_text_len

    @staticmethod
    def extract_text_content(html_node):
        return " ".join(str(html_node.text_content()).strip().split())

    def filter_by_css_classes(self, node):
        """
        Filter blocks by excluding certain blacklisted css classes
        :param node: 
        :return: True if block not blacklisted, False otherwise
        """
        css_classes = node.get('class')
        if css_classes:
            css_classes = css_classes.lower()
            css_classes = set(css_classes.split(' '))
            if len(css_classes) > 0:
                for blacklisted_class in self.class_blacklist:
                    for css_class in css_classes:
                        if blacklisted_class == css_class:
                            self.logger.info('css class blacklisted: {}'.format(css_class))
                            return False
                        elif blacklisted_class + '_' in css_class or blacklisted_class + '-' in css_class:
                            self.logger.info('css class blacklisted: {}'.format(css_class))
                            return False
        return True

    def filter_by_url(self, url):
        """
        Filter page based on a url blacklist
        :param url: 
        :return: True if url is blacklisted, False otherwise
        """
        for url_domain_clue in self.url_blacklist:
            if url_domain_clue in url:
                self.logger.info('url blacklisted')
                return True
        return False

    def content_is_valid(self, block, url):
        """
        Check content is not just simply a list of links list of links
        :param block:
        :return:  True if content is not a list of links, False otherwise
        """
        list_len = self.block_max_links  # avoid getting lists of links of minimum this length
        lists_of_links = self.isIndexPage.find_lists_of_links(block, url, list_len)
        lists_of_links = list(filter(lambda x: len(x) > list_len, lists_of_links))
        if len(lists_of_links) > 0:
            self.logger.info('content is list of links: not valid')
            return False
        else:
            return True

    def content_contains_product(self, text_content):
        """
        Check a block contains the product keyword
        :param text_content: the text content of a block
        :return: True if text_content contains the product, False otherwise
        """
        product_words = self.product.split(' ')
        product_bool = False
        for product_word in product_words:
            if product_word.lower() in text_content.lower():
                product_bool = True
        return product_bool

    def parse_valid_block(self, valid_block):
        """
        Supposes the first date is the post date
        Step 1: Identify the user node
        Step 2: Identify the highest level node containing the minimum text length
        but not containing the user node. This is the body node.
        Step 3: Extract the date
        
        :param valid_block: html node containing date, author and body information
        :return: {'date':'example_date', 'author':'example_author', 'body': 'example_body'}
        """
        valid_block_copy = deepcopy(valid_block)
        user_node, user_css_class, user_link, user_text = self.extract_user_node(valid_block_copy)
        node = valid_block_copy
        condition = True
        q = queue.Queue()
        q.put(node)
        # Normally at least one block has min required len and doesn't contain user class
        # Here we look for the block that contains just the user information but not date or author
        final_node = None
        while condition and not q.empty():
            node = q.get()
            children = node.getchildren()
            for child in children:
                contains_user_node = len(list(CSSSelector('.{}'.format(user_css_class))(child))) > 0
                valid_text_len = len(self.extract_text_content(child)) > self.min_text_len

                if not contains_user_node and valid_text_len:
                    final_node = child
                    condition = False
                    break
                elif valid_text_len and contains_user_node:
                    q.put(child)
                else:
                    pass
        if final_node is not None:
            text_content = self.extract_text_content(final_node)
            # Now consider html structure without the final node. Parse this to extract date
            final_node.getparent().remove(final_node)
        else:
            # Better to return too much text (i.e. with author and date) than none at all
            text_content = self.extract_text_content(valid_block)
        dates = self.extract_dates(valid_block_copy)
        dates = [date_tuple[0] for date_tuple in dates]
        dates = list(set(dates))
        if len(dates) > 1:
            self.logger.debug('multiple dates found: {}'.format(dates))
            date = dates[0]
        elif len(dates) == 1:
            date = dates[0]
        else:
            self.logger.debug('no dates found !')
            date = None
        parsed_dict = {
            'date': date,
            'author': user_text,
            'author_link': user_link,
            'body': text_content
        }
        return parsed_dict

    def find_lowest_valid_container(self, block):
        """
        Each block must contain an author, a post date and a text body
        We recursively traverse the html tree. For each node, we want to check if it is a valid container.
        A valid container has at least 2 valid blocks amongst its children.
        If we find at least 2 valid blocks, we consider the node to be a valid container.
        We then iterate the process on all the children nodes of the candidate valid container to see if we can find
        a valid container lower in the hierarchy.
        We proceed in a breadth first search fashion, and at the end, we return the lowest valid container we can find
        :param block: 
        :return: lowest_valid_container, which is an lxml node, and  None if it doesn't exist
        """
        # Init queue for breath first search over html node to find lowest valid container in html tree hierarchy
        q = queue.Queue()
        q.put(block)

        while_loop_bool = True
        lowest_valid_container = None
        while not q.empty() and while_loop_bool:
            node = q.get()  # These are potential valid containers
            if node is None:
                continue
            self.logger.debug(format_html_node_for_print(node, 'current node: '))
            # Blacklist certain classes
            css_check = self.filter_by_css_classes(node)
            if css_check is False:
                self.set_reason('css check is false')
                return False

            child_blocks = node.getchildren()
            child_blocks = [child for child in child_blocks if isinstance(child, etree._Element) and child.tag not in self.child_tag_blacklist]  # Filter out blocks (empirical criteria)
            if len(child_blocks) > 0:
                valid_block_count = 0
                valid_block_list = []
                for child in child_blocks:
                    self.logger.debug(format_html_node_for_print(child, 'child'))

                    if isinstance(child, etree._Comment):
                        continue
                    if self.is_valid_block(child):
                        valid_block_count += 1
                        valid_block_list.append(child)
                        self.logger.debug(format_html_node_for_print(child, 'valid child'))

                        if child.get('type') not in self.nodes_to_ignore and child is not None and child.tag not in self.tag_blacklist:
                            q.put(child)  # a child can only be valid if parent is valid

                if valid_block_count >= 2:
                    filtered_valid_blocks = [v for v in valid_block_list if self.filter_valid_blocks(v)]
                    if len(filtered_valid_blocks) >= 2:
                        for b in filtered_valid_blocks:
                            self.logger.debug(format_html_node_for_print(b, 'valid block'))
                        lowest_valid_container = node
                        self.logger.info(format_html_node_for_print(lowest_valid_container, 'lowest_valid_container'))
                        while_loop_bool = False
                        break

        if lowest_valid_container is not None:
            self.logger.info(format_html_node_for_print(lowest_valid_container, 'final lowest_valid_container'))
            return lowest_valid_container
        else:
            self.set_reason('no lowest_valid_container')
            return None

    def is_results_page(self, url, response=None):
        """
        :param url: a url (string) which will be used for a http request
        :param response: scrapy response can be passed directly to avoid redoing the request
        :return: true if page is a results page, false otherwise
        We search for certain structure:
        A page must contain at least 2 valid blocks
        These are html nodes which contain a date and a user
        as is always the case for forum posts and Q/A sites
        Step 1: (Re-)Initialise class and clean html
        Step 2: Identify lowest html node (container) which contains all the posts of the page (blocks)
        Step 3: Extract valid blocks from container
        Step 4: Filter valid blocks
        Step 5: Parse blocks to extract text content
        Step 6: Step 6 (optional): Filter on product, i.e. make sure at least one block contains the product keyword
        """
        # Step 1: (Re-)Initialise class and clean html
        self.url = url

        # make sure previous blocks are wiped
        self.text_content = []
        self.valid_blocks = []
        self.parsed_text_content = []
        self.is_pertinent = True

        html = get_html(url, base_path='html_pages/results_{}.html', response=response)
        original_html = deepcopy(html)
        html = self.get_body(html)
        if html is None:
            self.set_reason('no body')
            return False

        html = self.cleaner.clean_html(html)
        if html is None:
            self.set_reason('only js')
            return False

        self.html = html  # store html to later filter page for content

        # Check url is not blacklisted
        if self.filter_by_url(url):
            self.set_reason('url blacklisted')
            return False

        # Step 2: Identify lowest html node (container) which contains all the posts of the page (blocks)

        lowest_valid_container = self.find_lowest_valid_container(html)

        if lowest_valid_container is None:
            return False

        # Step 2b: Check for nested content
        # If 2 blocks are found, check if nested content inside second block
        # This is because the question and the answer  may be in different blocks
        # If nested content is found, flatten the structure

        self.logger.info("\n")

        child_blocks = list(filter(self.is_valid_block,
                                   lowest_valid_container.getchildren()))  # Initialise with child blocks of container

        self.logger.debug('child blocks count: {}'.format(len(child_blocks)))

        if len(child_blocks) == 2:
            snd_block = child_blocks[1]
            self.logger.debug(format_html_node_for_print(snd_block, 'snd block'))
            snd_lowest_valid_container = self.find_lowest_valid_container(snd_block)
            if snd_lowest_valid_container is not None:
                self.logger.info(format_html_node_for_print(snd_lowest_valid_container, 'snd_lowest_valid_container'))
                snd_child_blocks = list(filter(self.is_valid_block,
                                   snd_lowest_valid_container.getchildren()))
                child_blocks = [child_blocks[0]] + snd_child_blocks  # Flatten the structure
            else:
                self.logger.info('no snd_lowest_valid_container found')

        # Step 3: Extract valid blocks from container
        # The container may contain more content than we actually need
        # We go through each block and extract the lowest html node contain all essential information
        # i.e. author, date, body which respond to certain criteria
        # This is because usually the child node of a container doesn't correspond to the lowest level node containing the block
        # Each child block node tends to have multiple children nodes itself, but only one of these node usually tend to contain the actual block
        # We recursively work our way down the html tree of the block until we find the lowest node containing all the information a valid block should have
        # These new blocks are stored in the list new_child_blocks

        new_child_blocks = {}

        # For each block, extract the smallest valid node inside it
        # We construct a dictionary where the keys are the original child blocks and the values are the list of valid blocks in the hierarchy of the original child block
        # We then take the final element of this list to get the lowest block
        for index, child_block in enumerate(child_blocks):
            new_child_blocks[index] = [child_block]
            self.logger.debug(format_html_node_for_print(child_block, 'child'))
            exists_valid_grandchild = True
            while exists_valid_grandchild:
                children_count = len(child_block.getchildren())
                if children_count > 0:
                    invalid_children = 0
                    for grandchild_block in child_block.getchildren():
                        if self.is_valid_block(grandchild_block):
                            new_child_blocks[index].append(grandchild_block)  # We have found a new valid block lower down in the hierarchy
                            child_block = grandchild_block  # We iterate the search on the grandchild block to see if it has children again
                            break  # If we find a valid block, we stop looking at the other children and continue using this block
                        else:
                            invalid_children += 1
                if invalid_children == children_count:  # When all children of current block are invalid we exit the search
                    exists_valid_grandchild = False

        new_child_blocks = list(map(lambda x: x[-1], new_child_blocks.values()))

        # Step 4: Filter valid blocks
        # We re-run some checks over the block to check they are valid (text length, text content) and filter only valid blocks

        correct_post_len_count = 0
        for i, child in enumerate(new_child_blocks):
            self.logger.debug(format_html_node_for_print(child, 'child {}'.format(i)))
            child_copy = deepcopy(child)
            text_content = self.extract_text_content(child)
            self.logger.debug(text_content)

            text_len_bool = self.is_over_min_text_len(text_content, self.min_text_len) and self.is_under_max_text_len(text_content, self.max_text_len)
            valid_content_bool = self.content_is_valid(child, url)
            if text_len_bool and valid_content_bool:
                self.logger.debug(format_html_node_for_print(child, 'child {} is valid'.format(i)))
                correct_post_len_count += 1
                self.valid_blocks.append(child_copy)
                self.text_content.append(text_content)
                dates = self.extract_dates(child)
                self.logger.debug(list(dates))
                self.logger.info('\n')
            else:
                self.logger.debug(format_html_node_for_print(child, 'child {} is not valid'.format(i)))
                self.logger.debug('text_len_bool: {}'.format(text_len_bool))
                self.logger.debug('valid_content_bool: {}'.format(valid_content_bool))

        if correct_post_len_count < 2:
            self.set_reason('not enough valid posts found')
            return False

        self.logger.debug('valid blocks count (after step 4): {}'.format((correct_post_len_count)))

        # Step 5: Parse blocks to extract text content

        for block in self.valid_blocks:
            self.parsed_text_content.append(self.parse_valid_block(block))

        if len(self.parsed_text_content) < 2:
            self.set_reason('not enough valid blocks found')
            return False

        # Step 6 (optional): Filter on product, i.e. make sure at least one block contains the product keyword
        if self.product:
            product_keyword_count = 0
            for block in self.parsed_text_content:
                if self.content_contains_product(block['body']):
                    product_keyword_count += 1
            if product_keyword_count < 1:
                self.set_reason('is results page but product not mentioned')
                self.is_pertinent = False

        # If we make it to here, all the criteria are verified and we have a results page
        return True

if __name__ == "__main__":
    # For testing purposes
    results_page_url = "https://forums.macrumors.com/threads/iphone-6-touchscreen-goes-crazy.1853268/"
    product = None
    isResultsPage = IsResultsPage(product=product)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    print('source url', results_page_url)
    print('is results page bool: ', isResultsPage.is_results_page(results_page_url))
    print(isResultsPage.parsed_text_content)
    print('blocks count: ', len(isResultsPage.parsed_text_content))

