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

class TestIndex:
    # def test_is_result_page(self):
    #     results = []
    #     for url_pair in data:
    #         if url_pair[1]:
    #             html = get_html(url_pair[0])
    #             res = is_results_page(html, url_pair[0])
    #             print(url_pair[0],res == url_pair[1] )
    #             assert res == url_pair[1]
    #             results.append(res == url_pair[1])
    #     true_count = results.count(True)
    #     # print(true_count)
    #     # print(len(data))
    #     # assert len(data) == true_count

    # def test_is_positive_result_page(self):
    #     results = []
    #     site_domains = []
    #     for url_pair in data:
    #         domain = urlparse(url_pair[0]).netloc
    #         # print(domain)
    #         if domain not in site_domains:
    #             if url_pair[1]:
    #                 html = get_html(url_pair[0])
    #                 res = is_results_page(html, url_pair[0])
    #                 print(url_pair[0], res == url_pair[1])
    #                 assert res == url_pair[1]
    #                 results.append(res == url_pair[1])
    #         site_domains.append(domain)

    def test_is_negative_result_page(self):
        results = []
        # site_domains = []
        for url_pair in data:
            # print(url_pair[0], url_pair[1])
            # domain = urlparse(url_pair[0]).netloc
            # print(domain)
            # if domain not in site_domains:
            if not url_pair[1]:
                html = get_html(url_pair[0])
                res = is_results_page(html, url_pair[0])
                print(url_pair[0], res == url_pair[1])
                assert res == url_pair[1]
                results.append(res == url_pair[1])
            # site_domains.append(domain)





