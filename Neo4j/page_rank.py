#################################################
#  Author : Pierre COLOMBO                      #
#  Name : page_rank.py                          #
#                                               #
#  This file contains the PageRank and TFIDF    #
#  algorithms in cypther we use for our         #
#  predictions                                  #
#################################################

from neo4j.v1 import GraphDatabase, basic_auth,ClientError
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


def word_page_rank(unfiltered_query):
    '''
    Run a weighted page rank algorithms for nodes of type word, the weights are defined by the frequency of apparition
    of each word in documents
    :param unfiltered_query: the words you want to consider
    :return:
    '''

    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    stopword = set(stopwords.words('english'))
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))

    # Convert query as a list
    query = []
    for word in unfiltered_query.split() :
        word = stemmer.stem(word)
        if word not in stopword:
            if not word.isdigit():
                query.append(word)



    session = driver.session()
    session.run(
        "MERGE (word:Word) "
        "ON CREATE SET word.page_rank_sum = 0, word.Wpagerank = 0 "
        "ON MATCH SET word.page_rank_sum = 0, word.Wpagerank = 0")
    try :
        session.close()
    except AttributeError:
        pass



    session = driver.session()
    session.run(
        "MERGE (doc:Doc) "
        "ON CREATE SET doc.Wpagerank = 0, doc.page_rank_sum = 0 "
        "ON MATCH SET doc.Wpagerank = 0 , doc.page_rank_sum = 0")
    try :
        session.close()
    except AttributeError:
        pass

    session = driver.session()
        ### initialise the weight of the words to the sum of all incoming edges
    session.run("MATCH (word:Word)-[r]-(doc:Doc) "
                    "SET r.page_rank_weight = 0 "
                 , {"searchToken": query})
    try :
        session.close()
    except AttributeError:
        pass


    if True :
        session = driver.session()
        ### initialise the weight of the words to the sum of all incoming edges
        session.run("MATCH (word:Word) "
                    "WHERE word.name IN {searchToken} "
                    "WITH (word) as word "
                    "MATCH (word:Word)-[r]-(doc:Doc) "
                    "SET r.page_rank_weight = 1 "#r.frequency "
                 , {"searchToken": query})
        try :
            session.close()
        except AttributeError:
            pass


        session = driver.session()
        results = session.run("MATCH (word:Word) "
                    "WHERE word.name IN {searchToken} "
                    "WITH (word) as word "
                    "MATCH (word:Word)-[r]-(doc:Doc) "
                    "WITH word,doc, SUM(r.page_rank_weight) as word_sum " #change there not to have ...
                    "SET word.page_rank_sum = word_sum "
                              ,{"searchToken": query})
        try :
            session.close()
        except AttributeError:
            pass


        session = driver.session()
        results = session.run("MATCH (doc:Doc) "
                    "WITH (doc) as doc "
                    "MATCH (doc:Doc)-[r]-(word:Word) "
                    "WITH doc, SUM(r.page_rank_weight) as doc_sum "
                    "SET doc.page_rank_sum = doc_sum "
                              ,{"searchToken": query})


        try :
            session.close()
        except AttributeError:
            pass

    for i in range(50):
        session = driver.session()
        # http://people.cs.ksu.edu/~halmohri/files/weightedPageRank.pdf
        try :
            results = session.run("MATCH (a:Word) "
                        "WITH collect(distinct a) AS nodes, a.page_rank_sum AS DenomNormWin, COUNT(a) AS num_nodes "
                        "UNWIND nodes AS a "
                        "MATCH (a:Word)-[r]-(b:Doc) "
                        "WITH a,COLLECT(r) AS rels, r.page_rank_weight AS weight ,DenomNormWin, 1.0/num_nodes AS rank "
                        "UNWIND rels AS rel "
                    "SET endNode(rel).Wpagerank = "
                    "CASE "
                        "WHEN DenomNormWin > 0 THEN "
                            " endNode(rel).Wpagerank + weight*rank/(DenomNormWin) "
                        "ELSE endNode(rel).Wpagerank "
                    "END "

                    ",STARTNODE(rel).Wpagerank = "
                    "CASE "
                        "WHEN DenomNormWin > 0 THEN "
                            " startNode(rel).Wpagerank + weight*rank/(DenomNormWin) "
                        "ELSE startNode(rel).Wpagerank "
                    "END "
                        )

        except TimeoutError:
            pass

    normalize_attribute('Wpagerank')




def author_page_rank():
    '''
    Run a weighted page rank algorithms for nodes of type author, the weights are defined by the number of doc written
    by the author
    '''
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))

    ## initialise page_rank weights for author
    session = driver.session()
    session.run(
        "MERGE (author:Author) "
        "ON CREATE SET author.page_rank_sum = 0, author.Apagerank = 0 "
        "ON MATCH SET author.page_rank_sum = 0, author.Apagerank = 0")
    try :
        session.close()
    except AttributeError:
        pass


    ## initialise page_rank weights for doc
    session = driver.session()
    session.run(
        "MERGE (doc:Doc) "
        "ON CREATE SET doc.Apagerank = 0, doc.page_rank_sum = 0 "
        "ON MATCH SET doc.Apagerank = 0 , doc.page_rank_sum = 0")
    try:
        session.close()
    except AttributeError:
        pass



    ## initialise the weight of the edges to the number of docs
    session = driver.session()
    session.run("MATCH (author:Author) "
                    "MATCH (author:Author)-[r]-(doc:Doc) "
                    "SET r.page_rank_weight = author.number_of_docs ")
    try :
        session.close()
    except AttributeError:
        pass


    ## weight to normalize author side
    session = driver.session()
    session.run("MATCH (author:Author) "

                    "WITH (author) as author "
                    "MATCH (author:Author)-[r]-(doc:Doc) "
                    "WITH author,doc, SUM(r.page_rank_weight) as author_sum "
                    "SET author.page_rank_sum = author_sum ")
    try :
        session.close()
    except AttributeError:
        pass

    ## weight to normalize docs
    session = driver.session()
    session.run("MATCH (doc:Doc) "
                    "WITH (doc) as doc "
                    "MATCH (doc:Doc)-[r]-(author:Author) "
                    "WITH doc, SUM(r.page_rank_weight) as doc_sum "
                    "SET doc.page_rank_sum = doc_sum ")

    try :
        session.close()
    except AttributeError:
       pass

    for i in range(3):
        session = driver.session()
        # http://people.cs.ksu.edu/~halmohri/files/weightedPageRank.pdf
        results = session.run("MATCH (a:Author) "
                    "WITH collect(distinct a) AS nodes, a.page_rank_sum AS DenomNormWin, COUNT(a) AS num_nodes "
                    "UNWIND nodes AS a "
                    "MATCH (a:Author)-[r]-(b:Doc) "
                    "WITH a,COLLECT(r) AS rels, r.page_rank_weight AS weight ,DenomNormWin, 1.0/num_nodes AS rank "
                    "UNWIND rels AS rel "
                "SET endNode(rel).Apagerank = "
                "CASE "
                    "WHEN DenomNormWin > 0 THEN "
                        " endNode(rel).Apagerank + weight*rank/(DenomNormWin) "
                    "ELSE endNode(rel).Apagerank "
                "END "

                ",STARTNODE(rel).Apagerank = "
                "CASE "
                    "WHEN DenomNormWin > 0 THEN "
                        " startNode(rel).Apagerank + weight*rank/(DenomNormWin) "
                    "ELSE startNode(rel).Apagerank "
                "END "
                    )

    normalize_attribute('Apagerank')


def add_score(result_title,result_body) :
    '''
    This function add scores of the two lists
    :param result_title: list uid returned by the tf_idf corresponding to question.title containing the words
    :param result_body: list uid returned by the tf_idf corresponding to question.body containing the words
    :return: two list containing the score and the uid
    '''
    question_title_id = []
    question_title_score = []

    question_body_id = []
    question_body_score = []


    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
    for record in result_title:
        #print('id', record["id"])
        #print('tile', record["score"])
        session = driver.session()
        session.run("MATCH (doc:Doc) "
                    "WHERE doc.id = {id} "
                    "WITH doc "
                    "SET doc.solr_score = {score}", {"id": record["id"], "score": record["score"]})
        question_title_id.append(record["id"])
        question_title_score.append(record["score"])

        try:
            session.close()
        except AttributeError:
            pass



    for record in result_body:
        session = driver.session()
        session.run("MATCH (doc:Doc) "
                    "WHERE doc.id = {id} "
                    "WITH doc "
                    "SET doc.solr_score = {score}",{"id":record["id"],"score":record["score"]})
        question_body_id.append(record["id"])
        question_body_score.append(record["score"])

        try:
            session.close()
        except AttributeError:
            pass

    result_list_id = []
    result_list_score = []
    for body_id in question_body_id :
        if body_id in question_title_id :
            index_body = question_body_id.index(body_id)
            index_title = question_title_id.index(body_id)
            result_list_id.append(body_id)
            result_list_score.append(question_title_score[index_title] +question_body_score[index_body])
            del question_body_id[index_body]
            del question_body_score[index_body]
            del question_title_id[index_title]
            del question_title_score[index_title]

    result_list_id = result_list_id + question_body_id + question_title_id
    result_list_score = result_list_score + question_body_score + question_title_score
    ranking_id=[x for (y, x) in sorted(zip(result_list_score, result_list_id), reverse=True)]
    return ranking_id, sorted(result_list_score, reverse=True)



def comput_tf_idf(unfiltered_query,question_title_mutiplier,question_body_mutiplier):
    '''

    :param unfiltered_query: the unfiltered question you want to ask
    :param question_title_mutiplier: booster for the question_title field
    :param question_body_mutiplier: booster for the question_body field
    :return:
    '''
### See in https://graphaware.com/neo4j/2016/07/07/mining-and-searching-text-with-graph-databases.html

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
    session = driver.session()
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    stopword = set(stopwords.words('english'))

    query = []
    for word in unfiltered_query.split() :
        word = stemmer.stem(word)
        if word not in stopword:
            if not word.isdigit():
                query.append(word)



    ### Computer TF-IDF for the question
    result_title = session.run("MATCH (doc:Doc) "
                    "WITH count(doc) as NumberTotalOfDoc "
                    "MATCH (t:Word) "
                    "WHERE t.name IN {searchToken} "
                    "WITH t, NumberTotalOfDoc, {querySize} as QuerySize "
                    "MATCH (t)-[r:is_in_question_title]-(doc:Doc)"
                    "WITH t, count(distinct doc) as NumberOfDocWhereTAppears, NumberTotalOfDoc, QuerySize,doc "
                    "MATCH (t)-[r:is_in_question_title]-(doc:Doc) "
                    "WITH DISTINCT r,doc, t.name as name, sum(r.frequency)*(1 + log((1.0*NumberTotalOfDoc)/(NumberOfDocWhereTAppears + 1)))* (1.0/doc.length^0.5) as sum, QuerySize,(1.0/doc.length^0.5) as c "
                    "RETURN doc.id as id, {word_coefficient_question}*(1.0*size(collect(name))/QuerySize)*(sum(sum)) as score"
    ,{"searchToken": query,"querySize": len(query),"word_coefficient_question" : question_title_mutiplier})


    try:
        session.close()
    except AttributeError:
        pass




    session = driver.session()
    ### Computer TF-IDF for the question body
    result_body = session.run("MATCH (doc:Doc) "
                    "WITH count(doc) as NumberTotalOfDoc "
                    "MATCH (t:Word) "
                    "WHERE t.name IN {searchToken} "
                    "WITH t, NumberTotalOfDoc, {querySize} as QuerySize "
                    "MATCH (t)-[r:is_in_question_body]-(doc:Doc)"
                    "WITH t, count(distinct doc) as NumberOfDocWhereTAppears, NumberTotalOfDoc, QuerySize,doc "
                    "MATCH (t)-[r:is_in_question_body]-(doc:Doc) "
                    "WITH DISTINCT r,doc, t.name as name, sum(r.frequency)*(1 + log((1.0*NumberTotalOfDoc)/(NumberOfDocWhereTAppears + 1)))* (1.0/doc.length^0.5) as sum, QuerySize,(1.0/doc.length^0.5) as c "
                    "RETURN doc.id as id, {word_coefficient_answer}*(1.0*size(collect(name))/QuerySize)*(sum(sum)) as score"
    ,{"searchToken": query,"querySize": len(query),"word_coefficient_answer" : question_body_mutiplier})


    try:
        session.close()
    except AttributeError:
        pass


    return add_score(result_body,result_title)


def normalize_attribute(attribute_name) :
    '''
    This function normalize PageRank attributes
    :param attribute_name: The name of the attribute you want to normalize
    '''
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
    session = driver.session()

    if attribute_name == 'Apagerank' :
        results = session.run("START n=node(*) "
                                   "WHERE EXISTS(n.Apagerank) "
                                   "RETURN n, n.Apagerank ORDER BY n.Apagerank DESC LIMIT 1"
                                   ,{"attribute_name" : attribute_name})
        for record in results :
            max = record[1]

        try:
            session.close()
        except AttributeError:
            pass

        session = driver.session()

        results = session.run("START n=node(*) "
                              "WHERE EXISTS(n.Apagerank) "
                              "SET n.Apagerank = n.Apagerank/{max} "
                              , {"max": max})
        try:
            session.close()
        except AttributeError:
            pass

    if attribute_name == 'Wpagerank' :
        results = session.run("START n=node(*) "
                              "WHERE EXISTS(n.Wpagerank) "
                              "RETURN n, n.Wpagerank ORDER BY n.Wpagerank DESC LIMIT 1"
                              , {"attribute_name": attribute_name})
        for record in results:
            max = record[1]
        try:
            session.close()
        except AttributeError:
            pass

        session = driver.session()

        results = session.run("START n=node(*) "
                              "WHERE EXISTS(n.Wpagerank) "
                              "SET n.Wpagerank = n.Wpagerank/{max} "
                              , {"max": max})
        try:
            session.close()
        except AttributeError:
            pass






#print(comput_tf_idf('List of damaged files from chkdsk process',1,1))

#author_page_rank()
#word_page_rank('List of damaged files from chkdsk process')

