from solr_query import SolrQuery
import pandas as pd
import json
solquery = SolrQuery('localhost:8983' ,'ProductDB')
file = open('research_words' ,'r')
s = file.read()
solquery.__set_near_query__('question.question_title:' ,str(s) ,10 ,10)
#solquery.add_field('question.question_title')
solrResponse = solquery.execute().get_results()
print(solrResponse)
with open('data.json', 'w') as outfile:
    jsonFile =json.dumps(solrResponse)
    outfile.write(jsonFile)



j