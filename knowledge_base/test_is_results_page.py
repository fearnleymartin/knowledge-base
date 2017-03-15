import csv
import pytest
from is_results_page import is_results_page, get_html
from is_index_page import is_index_page
from urllib.parse import urlparse



data = []
with open('BDD-Q-A.csv','r') as csvfile:
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

    def test_is_result_page(self):
        results = []
        count = 0
        for url_pair in data:
            url, label = url_pair[0], url_pair[1]
            domain = urlparse(url).netloc
            if domain not in self.domains_to_skip:
                # if label:
                res = is_results_page(url)
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
                    res = is_results_page(url)
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
                    res = is_results_page(url)
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




