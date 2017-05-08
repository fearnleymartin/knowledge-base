#################################################
#  Author : Pierre COLOMBO                      #
#  Name : baseline_model.py                     #
#                                               #
#  Contains the baseline algorithms we use      #
#  to query the neo4j DataBase                  #
#################################################


from Neo4j.page_rank import word_page_rank,author_page_rank,comput_tf_idf
import string
from neo4j.v1 import GraphDatabase, basic_auth,ClientError
from nltk.corpus import stopwords


def filter_raw_query(raw_query) :
    '''
    Filter the query with stop words and return a list
    '''
    filtered_words = [word for word in raw_query.split() if word not in stopwords.words('english')]
    raw_query = []
    for word in filtered_words :
        raw_query.append(word)

    return raw_query


def find_best_doc_tf(unfiltered_query,question_title_mutiplier,question_body_mutiplier):
    '''

    Return a list of best documents according to the TF_IDF and the list of a score (2 uple)
    :param unfiltered_query: the unfiltered question you want to ask
    :param question_title_mutiplier: booster for the question_title field
    :param question_body_mutiplier: booster for the question_body field

    '''
    return comput_tf_idf(unfiltered_query,question_title_mutiplier,question_body_mutiplier)


def find_best_doc_page_rank(query,number_of_result, coefficientAuthor=1, coefficientWord=1) :
    '''

    :param query: the unfiltered question you want to ask
    :param number_of_result: recal
    :param coefficientAuthor: booster for the author PageRank result
    :param coefficientWord: booster  for the word PageRank result
    :return:
    '''
    l_uid = []
    author_page_rank()
    word_page_rank(query)
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))

    session = driver.session()
    session.run("MATCH (doc:Doc) "
                "SET doc.Fpagerank = 0 "
    )
    try:
        session.close()
    except AttributeError:
        pass

    session = driver.session()
    session.run("MATCH (doc:Doc) "
                "SET doc.Fpagerank = {coefficient_author} * doc.Wpagerank   + {coefficient_word} * doc.Apagerank "
                , {"coefficient_author": coefficientAuthor, "coefficient_word": coefficientWord})
    try:
        session.close()
    except AttributeError:
        pass

    session = driver.session()
    result = session.run("START n=node(*) WHERE EXISTS(n.Fpagerank) "
                "RETURN n.id AS id, n.Fpagerank ORDER BY n.Fpagerank DESC LIMIT {number_of_result} "
                , {"number_of_result": number_of_result})
    try:
        session.close()
    except AttributeError:
        pass

    for record in result:
        l_uid.append(record['id'])

    return l_uid