import csv
import pytest
# try:
#     from ..knowledge_base.scripts.is_results_page import is_results_page
#     # get_html
# except Exception:
from knowledge_base.knowledge_base.scripts.is_results_page import IsResultsPage
from urllib.parse import urlparse

results_output_path = 'results_output.csv'
items_output_path = 'items_output.jl'

data = []
with open('BDD-Q-A_with_extra_criteria.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if 'Yes' in row[1]:
            row[1] = True
        else:
            row[1] = False
        data.append(row)

class TestResultsPage:

    # js problem for symantec
    domains_to_skip = ['www.symantec.com']
    isResultsPage = IsResultsPage()

    def test_is_result_page(self):
        print("started")
        results = []
        count = 0
        with open(items_output_path, 'w') as f_items:
            with open(results_output_path, 'w') as f_results:
                for url_pair in data:
                    url, label = url_pair[0], url_pair[1]
                    domain = urlparse(url).netloc
                    if domain not in self.domains_to_skip:
                        # if label:
                        res = self.isResultsPage.is_results_page(url)
                        print(url, res == label)
                        print('--------------------------------------------------------------------------------------')
                        # assert res == label
                        results.append(res == label)
                        count += 1
                        f_results.write('{},{}\n'.format(url, res))
                        item = {url: self.isResultsPage.parsed_text_content}
                        try:
                            f_items.write('{}\n'.format(item).replace('\u2191', '').replace('\U0001f44d', ''))
                        except UnicodeEncodeError:
                            # print('{}\n'.format(item).replace('\u2191', ''))
                            f_items.write('{}'.format({url: 'unicode error'}))

        true_count = results.count(True)
        print(true_count)
        print(count)
        expected_count = count
        assert expected_count == true_count

    def test_is_positive_result_page(self):
        results = []
        count = 0
        site_domains = self.domains_to_skip + ['']
        for url_pair in data:
            url, label = url_pair[0], url_pair[1]
            domain = urlparse(url).netloc
            # print(domain)
            if domain not in site_domains:
                if label:
                    res = self.isResultsPage.is_results_page(url)
                    print(url, res == label)
                    print('--------------------------------------------------------------------------------------')

                    # assert res == label
                    results.append(res == label)
                    count += 1
            site_domains.append(domain)
        true_count = results.count(True)
        print(true_count)
        print(count)
        expected_count = count
        assert expected_count == true_count

    def test_is_negative_result_page(self):
        results = []
        count = 0
        for url_pair in data:
            url, label = url_pair[0], url_pair[1]
            domain = urlparse(url).netloc
            if domain not in self.domains_to_skip:
                if not label:
                    res = self.isResultsPage.is_results_page(url)
                    print(url, res == label)
                    print('--------------------------------------------------------------------------------------')

                    # assert res == label
                    results.append(res == label)
                    count += 1
        true_count = results.count(True)
        print(true_count)
        print(count)
        expected_count = count
        assert expected_count == true_count


if __name__ == "__main__":
    t = TestResultsPage()
    t.test_is_result_page()

