import csv
import pytest
# try:
#     from ..knowledge_base.scripts.is_results_page import is_results_page
#     # get_html
# except Exception:
from knowledge_base.knowledge_base.scripts.is_results_page import IsResultsPage
from urllib.parse import urlparse

item_count_path = 'items_count.csv'

data = []
with open('BDD-Q-A_count.csv','r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if 'Yes' in row[1] or 'No' in row[1]:
            pass
        else:
            data.append(row)

class TestResultsParsing:

    # js problem for symantec
    domains_to_skip = ['www.symantec.com']
    isResultsPage = IsResultsPage()

    def test_result_page_parsing_count(self):
        print("started")
        results = []
        count = 0
        with open(item_count_path, 'w') as f_count:
            for url_pair in data:
                url, label = url_pair[0], int(url_pair[1])
                domain = urlparse(url).netloc
                if domain not in self.domains_to_skip:

                    res = self.isResultsPage.is_results_page(url)
                    items_count = len(self.isResultsPage.parsed_text_content)
                    print(url, items_count == label)
                    print('--------------------------------------------------------------------------------------')
                    results.append(items_count == label)
                    count += 1
                    item = '{},{},{}'.format(url, label, items_count)
                    f_count.write('{}\n'.format(item))
        true_count = results.count(True)
        print(true_count)
        print(count)
        expected_count = count
        assert expected_count == true_count




if __name__ == "__main__":
    t = TestResultsParsing()
    t.test_result_page_parsing_count()

