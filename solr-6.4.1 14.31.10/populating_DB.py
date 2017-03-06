from solr_query import SolrQuery
solquery = SolrQuery('localhost:8983','ProductDB')

solquery.add_doc('Old_file/Second_Pipeline/superuser_items.json')


#solquery.clean_DB()


