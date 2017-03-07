import unittest
import sys

sys.path.append('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10')
from solr_query import SolrQuery
from SolrEvaluation.evaluation_f1_score import f1_score


class Test_SolrQuery(unittest.TestCase) :
    def test_cleanDB(self):

        solquery = SolrQuery('localhost:8983', 'TestCore')
        response = solquery.clean_DB()
        succeed = False
        if ">0</int><int" in str(response):
            succeed = True

        self.assertTrue(succeed)


    def test_add_doc(self):

        solquery = SolrQuery('localhost:8983', 'TestCore')
        response = solquery.add_doc('Old_file/Second_Pipeline/superuser_items.json')
        succeed = False
        if "1 files indexed" in response :
            succeed = True

        self.assertTrue(succeed)


    def test_set_query(self):
        # prepare the environment
        solquery = SolrQuery('localhost:8983', 'TestCore')
        solquery.clean_DB()
        solquery.add_doc('Old_file/Second_Pipeline/superuser_items.json')

        #perform the query
        s = "virus"
        solquery.set_query('question.question_title:' + s)
        solquery.add_field('question.question_title')
        solrResponse = solquery.execute().get_results()
        #expected response
        theoritical_response = [{'question.question_title': 'How do anti-viruses work?'},
                                {'question.question_title': 'How do anti-viruses work?'},
                                {'question.question_title': 'How do anti-viruses work?'},
                                {'question.question_title': 'How do anti-viruses work?'},
                                {'question.question_title': 'How do anti-viruses work?'}, {
                                    'question.question_title': 'How can I explain what a computer virus is to people who are not familiar with computers and programming?'},
                                {
                                    'question.question_title': 'How can I explain what a computer virus is to people who are not familiar with computers and programming?'},
                                {
                                    'question.question_title': 'How can I explain what a computer virus is to people who are not familiar with computers and programming?'},
                                {
                                    'question.question_title': 'How can I explain what a computer virus is to people who are not familiar with computers and programming?'},
                                {
                                    'question.question_title': 'How can I explain what a computer virus is to people who are not familiar with computers and programming?'}]

        self.assertEqual(theoritical_response,solrResponse)

    def test_set_query_2(self):
        # prepare the environment
        solquery = SolrQuery('localhost:8983', 'TestCore')
        solquery.clean_DB()
        solquery.add_doc('Old_file/Second_Pipeline/superuser_items.json')

        # perform the query
        s = "2809"
        solquery.set_query('question.question_view_count:' + s)
        solquery.add_field('question.question_view_count')
        solrResponse = solquery.execute().get_results()
        # expected response
        theoritical_response = [{'question.question_view_count': 2809}, {'question.question_view_count': 2809},
                                {'question.question_view_count': 2809}, {'question.question_view_count': 2809},
                                {'question.question_view_count': 2809}]

        self.assertEqual(theoritical_response, solrResponse)



class Test_evaluation_f1_score(unittest.TestCase):

    def test_f1_score(self):
        self.assertEqual(f1_score('\"Outlook reminders not appearing\"', 'ProductDB', '8983', 'superuser.com'),1.0)





if __name__ == '__main__':
    unittest.main()

