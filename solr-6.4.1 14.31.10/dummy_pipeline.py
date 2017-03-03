from solr_query import SolrQuery
import pandas as pd
import json
solquery = SolrQuery('localhost:8983' ,'ProductDB')
file = open('research_words' ,'r')
s = file.read()
print('question.question_title:'+s)
solquery.set_query('question.question_title:'+s)
#solquery.__set_near_query__('question.question_title:' ,str(s) ,1 ,1)
solquery.add_field('question.question_title')
solrResponse = solquery.execute().get_results()
print(solrResponse)
