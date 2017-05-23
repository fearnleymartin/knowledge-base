import csv
from knowledge_base.knowledge_base.scripts.is_results_page import IsResultsPage
from urllib.parse import urlparse

input_file = 'evaluation_set.csv'


results_output_path = 'results_output.csv'
items_output_path = 'items_output.jl'
item_count_path = 'items_count.csv'

data = []
with open(input_file,'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if 'Yes' in row[1] or 'No' in row[1]:
            pass
        else:
            data.append(row)


class TestResultsPage(object):
    """
    In the input file we define a list of pages labelled with the number of question/answer pairs they contain
    We evaluate the algorithm over the dataset for both the classification and parsing problem
    For the classification problem: A page classified as a results page should have a positive number  of question/answer pairs and vice versa.
    For the parsing problem, we count the number of pages for which all the posts were correctly identified.
    We track three outputs:
    - The items (question_answer pairs returned for each pages) (in items_output_path)
    - The classification results (results_output_path)
    - The number of identified posts (item_count_path)
    """
    isResultsPage = IsResultsPage()

    def test_is_result_page(self):
        results_classification = []
        results_parsing = []
        page_count = 0
        results_page_count = 0
        with open(items_output_path, 'w') as f_items:
            with open(results_output_path, 'w') as f_results:
                with open(item_count_path, 'w') as f_count:
                    for url_pair in data:
                        url, expected_count = url_pair[0], int(url_pair[1])
                        if expected_count == 0: label = False
                        else:
                            label = True
                            results_page_count += 1
                        domain = urlparse(url).netloc
                        res = self.isResultsPage.is_results_page(url)
                        print(url, res == label)
                        if label:
                            actual_count = len(self.isResultsPage.parsed_text_content)
                            print(url, actual_count == expected_count, expected_count, actual_count)
                            results_parsing.append(actual_count == expected_count)
                            item = '{},{},{}'.format(url, expected_count, actual_count)
                            f_count.write('{}\n'.format(item))

                        results_classification.append(res == label)
                        f_results.write('{},{}\n'.format(url, res))
                        item = {url: self.isResultsPage.parsed_text_content}
                        try:
                            f_items.write('{}\n'.format(item).replace('\u2191', '').replace('\U0001f44d', ''))
                        except UnicodeEncodeError:
                            f_items.write('{}'.format({url: 'unicode error'}))
                        page_count += 1
                        print('--------------------------------------------------------------------------------------')

        print('Classification:')
        true_count_classification = results_classification.count(True)
        print('True count: {}, count: {}'.format(true_count_classification, page_count))
        print('Parsing:')
        true_count_parsing = results_parsing.count(True)
        print('True count: {}, count: {}'.format(true_count_parsing, results_page_count))


if __name__ == "__main__":
    t = TestResultsPage()
    t.test_is_result_page()

