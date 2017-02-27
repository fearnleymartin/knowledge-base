import os
import sys
from urllib.request import urlopen

core_name = 'ProductDB'
port = '8983'
document_path = 'server/solr/ProductDB/testSimpler.json'

'''
Ajouter un doc ....

if len(sys.argv) > 0:
    os.chdir('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10/')
    print(os.getcwd())
    os.system('bin/post -c ' + core_name + ' ' + document_path)
'''


#Perform a query on the collection
def search_query(q_keyword='*:*',fiel_name='',k_fiel_name=''):
    url = 'http://localhost:' + port + '/solr/' + core_name + '/select?q=' + q_keyword + '&wt=python&rows=10000000&'+fiel_name+'='+k_fiel_name
    print(url)
    connection = urlopen(url)
    response = eval(connection.read())
    n_found = response['response']['numFound']
    print(n_found)
    results = response['response']['docs']
    print(results)
    return results

#Perform a query on the collection
def search_query2(q_keyword='*:*',fiel_name='',k_fiel_name=''):
    url = 'http://localhost:' + port + '/solr/' + core_name + '/select?q=' + q_keyword + '&wt=python&rows=10000000&'
    print(url)
    connection = urlopen(url)
    response = eval(connection.read())
    n_found = response['response']['numFound']
    print(n_found)
    results = response['response']['docs']
    print(results)
    return results


def clean_DB() :

    if len(sys.argv) > 0:
        os.chdir('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10/')
        print(os.getcwd())
        os.system('bin/post -c ' + core_name + ' ' + '< delete > < query > *: * < / query > < / delete >')

    return

clean_DB()


#search_query('*:*','question.question_body','2019-10-15:13:03:00')

