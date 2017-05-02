#################################################
#  Author : Pierre COLOMBO                      #
#  Name : populating_DB.py                      #
#                                               #
#  This script is used to put your docs into    #
#  SOLR for the evaluation                      #
#################################################


from solr_query import SolrQuery
SOLR_CORE_NAME = 'Evaluation'
SOLR_ADRESSE  = 'localhost:8983'
DOCPATH = 'Old_file/EvaluationDB/duplicates_and_original_questions.json'

## Creating SolrQuery object, this object will be used for all our query
solquery = SolrQuery(SOLR_ADRESSE,SOLR_CORE_NAME)

## Cleaning the database from all previous documents
solquery.clean_DB()

## Posting the jsonline we want to put into solr
solquery.add_doc(DOCPATH)




