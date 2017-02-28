from solr_query import SolrQuery
solquery = SolrQuery('localhost:8983' ,'ProductDB')
file = open('research_words' ,'r')
s = file.read()
solquery.__set_near_query__('question.question_title:' ,str(s) ,10 ,10)
print( 'question.question_title:'+ '\''+ str(s) + '\'')
solquery.add_field('question.question_title')
solrResponse = solquery.execute()
print(solrResponse.get_results())
