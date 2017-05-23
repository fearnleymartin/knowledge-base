from knowledge_base.knowledge_base.scripts.is_index_page import IsIndexPage
import csv

"""
True urls are index pages, false urls are not
We check we can classify them correctly
"""

true_urls = [
    'https://www.reddit.com/r/iphonehelp/',
    'https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/',
    'https://discussions.apple.com/search.jspa?currentPage=1&includeResultCount=true&q=outlook+problems',  # JS problems
    'https://forum.eset.com/forum/49-general-discussion/',
    'https://community.spiceworks.com/windows?source=navbar-subnav',
    'https://github.com/jitsi/jitsi/issues',
    'http://forum.mailenable.com/viewforum.php?f=2&sid=805e9ea1611daf70a515c16519f48513'
    'https://forums.adobe.com/community/acrobat/acrobat_windows/content?filterID=contentstatus%5Bpublished%5D~objecttype~objecttype%5Bthread%5D',
    'https://community.mindjet.com/mindjet/topics/search/show',
    'https://www.symantec.com/connect/endpoint-management/forums/helpdesk-solution',  # JS problem
    'https://www.petri.com/forums/forum/client-operating-systems/windows-10',
    'http://en.community.dell.com/support-forums/laptop/f/3518',
    'http://stackoverflow.com/questions',
    'https://community.sharefilesupport.com/citrixsharefile/topics/search/show',
    'http://www.dslreports.com/forum/svendors',  # pagination problem
    'https://community.sharefilesupport.com/citrixsharefile/topics/search/show',
    'https://community.dynamics.com/crm/f/117',
]

false_urls = [
    'https://docs.python.org/3/library/urllib.parse.html',
    'https://support.wix.com/en/ticket/c80d73fd-0599-4b07-a766-440ee5a6c720',
    'https://www.petri.com/forums/forum',  # Kinda of in the middle # latest post problem
    'https://www.symantec.com/connect/forums/community-forums',
    'http://forum.mailenable.com/index.php?sid=0c01a20381b4418301f6c699e1074236',
    'http://en.community.dell.com/support-forums/laptop/f/3518/t/19676610',
    'http://coindesk.com',
    'http://bbc.com',  # still fails
    'http://swisscom.ch',
    'http://epfl.ch',
    'http://facebook.com',
    'http://google.com',
    'http://github.com',
    'http://stackoverflow.com',  #  Kind of yes and no. Does have an index, but not on a specific topic...
    'http://forums.macrumors.com',

]


class TestIndex(object):
    isIndexPage = IsIndexPage()
    def test_positives(self):
        """Check we correctly identified index pages"""
        true_count = 0
        for url in true_urls:
            res = self.isIndexPage.is_index_page(url)
            print(res, url)
            if res:
                true_count += 1
        print('true count: {}, total count: {}, accuracy: {}'.format(true_count, len(true_urls),true_count/len(true_urls)))

    def test_negatives(self):
        """Check we correctly identify non-index pages"""
        false_count = 0
        for url in false_urls:
            res = self.isIndexPage.is_index_page(url)
            print(res, url)
            if not res:
                false_count += 1
        print('false count: {}, total count: {}, accuracy: {}'.format(false_count, len(false_urls),false_count/len(false_urls)))

    def test_results_pages_are_not_classified_as_index_pages(self):
        """
        Check results page are not classified as index pages
        """
        results_page_urls = []
        input_file = 'evaluation_set.csv'
        with open(input_file) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                if int(row[1]) > 0:  # we only take results pages
                    results_page_url = row[0]
                    results_page_urls.append(results_page_url)
        results = []
        for results_page_url in results_page_urls:
            res = self.isIndexPage.is_index_page(results_page_url)
            print(results_page_url, res is False)
            results.append(res is False)
        true_count = results.count(True)
        print('true count: {}, total count: {}, accuracy: {}'.format(true_count, len(true_urls),true_count/len(true_urls)))


if __name__ == "__main__":
    test_index = TestIndex()
    # test_index.test_positives()
    test_index.test_negatives()
    # test_index.test_results_pages_are_not_classified_as_index_pages()