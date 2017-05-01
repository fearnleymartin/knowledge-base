#################################################
#  Author : Pierre COLOMBO                      #
#  Name : build_databese.py                     #
#                                               #
#  Script for filling neo4j DataBase            #
#################################################

from neo4j.v1 import GraphDatabase, basic_auth,ClientError
import neo4j.v1
import json
from nltk.corpus import stopwords
import uuid
import string
import re
import string
from nltk.stem.snowball import SnowballStemmer
import pandas as pd

if __name__ == 'main':
    # Constants :
    number_of_doc =10000  # number of docs you want to post
    error = 0 # number of errors
    i=0


    # set stemmer to english
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    stopwords = set(stopwords.words('english'))


    # Connection to Neo4j DB
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
    session = driver.session()

    # Delete all existing nodes
    session.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

    # Post the docs
    with open('../solr-6.4.1 14.31.10/Old_file/EvaluationDB/duplicates_and_original_questions.json') as f:
        for line in f:

            # after n documents we break
            if(i ==number_of_doc ):
                break
            i+=1
            print('document number is : ', str(i))


            d = json.loads(line)
            doc_uid = d['uid']

            # Question Body
            question_body = d['question']['question_body']

            # Question Title
            question_title = d['question']['question_title']

            # Remove url
            question_title = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', question_title)
            question_body = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', question_body)

            # Remove punctuation
            question_body = "".join(l for l in question_body if l not in string.punctuation)
            length = len(question_body)

            question_title = "".join(l for l in question_title if l not in string.punctuation)
            length += len(question_body)

            # Q/A attributs
            question_view_count = d['question']['question_view_count']
            answer_upvotes =  d['answer']['answer_upvotes']

            session.run("CREATE (a:Doc {id: {id}, question_view_count: {question_view_count},length:{length}, answer_upvotes: {answer_upvotes}})",
                         {"question_view_count": str(question_view_count),"answer_upvotes":str(question_view_count),"id" :doc_uid,"length":length })


            # Author of the question
            question_author_name = d['question']['question_author']['author_name']
            session.run("MERGE (a:Author {name : {name} }) ON CREATE SET a.number_of_docs = 1 ON MATCH SET a.number_of_docs  =a.number_of_docs  + 1 ",
                         {"name": question_author_name})

            session.run("MATCH (myDoc:Doc { id:  {id}  }),(myAuthor:Author { name: {answer_author_name} }) MERGE (myAuthor)-[r:is_author]-(myDoc)",
                        {"answer_author_name": question_author_name,"id" :doc_uid})



            for word in question_title.split() :
                if word not in stopwords :
                    if not word.isdigit() :
                        if len(word) > 3 :
                            word = stemmer.stem(word)
                            print(word)
                            try :
                                session.run("MERGE (a:Word {name : {name} })",
                                                {"name": word})
                                session.run(
                                    "MATCH (myDoc:Doc { id:  {id}  }),(myWord:Word { name: {name} }) MERGE (myWord)-[r:is_in_question_title]-(myDoc) ON CREATE SET r.frequency =  {frequency} ON MATCH SET r.frequency = r.frequency + {frequency}",
                                        {"name": word,"id" :doc_uid,"frequency":1})
                            except ClientError:
                                print('error',word)
                                error +=1

            for word in question_body.split() :
                if word not in stopwords :
                    if not word.isdigit() :
                        if len(word) > 3 :
                            word = stemmer.stem(word)
                            print(word)
                            try :
                                session.run("MERGE (a:Word {name : {name} })",
                                                {"name": word})
                                session.run(
                                    "MATCH (myDoc:Doc { id:  {id}  }),(myWord:Word { name: {name} }) MERGE (myWord)-[r:is_in_question_body]-(myDoc) ON CREATE SET r.frequency =  {frequency} ON MATCH SET r.frequency = r.frequency + {frequency}",
                                        {"name": word,"id" :doc_uid,"frequency":1})
                            except ClientError:
                                print('error',word)
                                error +=1






    try :
        session.close()
        print('number of error '+ str(error))

    except AttributeError :
        print('finished')
        print('number of error ' + str(error))

    except neo4j.exceptions.ClientError :
        print('ERROR NEO4J closing')

