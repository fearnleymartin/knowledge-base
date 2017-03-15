from is_index_page import is_index_page, get_html
from is_results_page import get_html as get_html_results
import pytest
import csv

"""
True urls are index pages, false urls are not
We check we can classify them correctly
"""

true_urls = [
    'https://www.reddit.com/r/iphonehelp/',
    'https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/',
    # 'https://discussions.apple.com/search.jspa?currentPage=1&includeResultCount=true&q=outlook+problems',  # JS problems
    'https://forum.eset.com/forum/49-general-discussion/',
    'https://community.spiceworks.com/windows?source=navbar-subnav',
    'https://github.com/jitsi/jitsi/issues',
    'http://forum.mailenable.com/viewforum.php?f=2&sid=805e9ea1611daf70a515c16519f48513'
    'https://forums.adobe.com/community/acrobat/acrobat_windows/content?filterID=contentstatus%5Bpublished%5D~objecttype~objecttype%5Bthread%5D',
    'https://community.mindjet.com/mindjet/topics/search/show',
    # 'https://www.symantec.com/connect/endpoint-management/forums/helpdesk-solution',  # JS problem
    'https://www.petri.com/forums/forum/client-operating-systems/windows-10',
    'http://en.community.dell.com/support-forums/laptop/f/3518',
    'http://stackoverflow.com/questions',
    'https://community.sharefilesupport.com/citrixsharefile/topics/search/show',
    # 'http://www.dslreports.com/forum/svendors',  pagination problem
    'https://community.sharefilesupport.com/citrixsharefile/topics/search/show',
    'https://community.dynamics.com/crm/f/117',
]
# true_urls = []

false_urls = [
    'https://docs.python.org/3/library/urllib.parse.html',
    'https://support.wix.com/en/ticket/c80d73fd-0599-4b07-a766-440ee5a6c720',
    # TODO: investigate
    'https://www.petri.com/forums/forum',  # Kinda of in the middle # latest post problem
    'https://www.symantec.com/connect/forums/community-forums',
    'http://forum.mailenable.com/index.php?sid=0c01a20381b4418301f6c699e1074236',
    'http://en.community.dell.com/support-forums/laptop/f/3518/t/19676610',
    'http://coindesk.com',
    # TODO: investigate
    'http://bbc.com',  # still fails
    'http://swisscom.ch',
    'http://epfl.ch',
    'http://facebook.com',
    'http://google.com',
    'http://github.com',
    # @TODO: add extra filter of checking whether page is relevant to topic/product
    'http://stackoverflow.com',  #  Kind of yes and no. Does have an index, but not on a specific topic...
    'http://forums.macrumors.com',

]


class TestIndex:
    def test_is_index_page(self):
        """Check we correctly identified index pages"""
        for url in true_urls:
            res = is_index_page(url)
            print(res, url)
            assert(res)

    def test_is_not_index_page(self):
        """Check we correctly identify non-index pages"""
        for url in false_urls:
            res = is_index_page(url)
            print(res, url)
            assert(not res)

    def test_is_not_index_page2(self):
        """
        Check results page are not classified as index pages
        :return:
        """
        results_page_urls = []
        input_file = 'BDD-Q-A.csv'
        with open(input_file) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                if 'Yes' in row[1]:  # we only take results pages
                    results_page_url = row[0]
                    results_page_urls.append(results_page_url)
        results = []
        for results_page_url in results_page_urls:
            res = is_index_page(results_page_url)
            # assert
            print(results_page_url, res is False)
            results.append(res is False)
        true_count = results.count(True)
        print(true_count)
        print(len(results_page_urls))
        assert len(results_page_urls) == true_count