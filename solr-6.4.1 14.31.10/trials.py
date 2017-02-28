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

import json
#Perform a query on the collection
def search_query2():
    url = 'http://localhost:8983/solr/ProductDB/select?_=1488287583061&defType=edismax&q=*:*&q.alt=Forms+on+Outlook+for+Mac&qf=question.question_title&wt=json'
    print('url is '+url)
    connection = urlopen(url)
    response = json.loads(connection.read().decode('utf-8'))
    #response = exec(response)
    results = response
    print(results)
    return results



search_query2()
