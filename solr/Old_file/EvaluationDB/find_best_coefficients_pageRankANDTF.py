import os
import pandas as pd
import sys
import numpy as np

from Neo4j.baseline_model import find_best_doc_page_rank,find_best_doc_tf

def find_first_match(input_dataFrame,ref_uid,recall_at):
    ''' Return the position of the first match with the uid
    If first match is greater than recall_at the number is recall_at + 1
    If the is no match return recallat + 2
    '''
    try :
        number = input_dataFrame.uid[input_dataFrame.uid == ref_uid ].index.tolist()[0]
        if number > recall_at :
            number = recall_at + 1

    except IndexError :
        number = recall_at + 2
    return number

def compute_recall(uid_list ,number_of_uid ,recall_at) :
    ''' Given a list of uid return the recall
    '''
    count = 0
    for e in uid_list :
        if  e < recall_at + 1 :
            count +=1

    return count / number_of_uid

# Usefull functions to perform basic statistics
def compteNumberOfMiss(l):
    count = 0
    for e in l:
        if e > recall_at :
            count +=1
    return count

def mean(l):
    mean = 0
    for e in l:
        if e > recall_at :
            pass
        else :
            mean += e
    if len(l)-compteNumberOfMiss(l) != 0 :
        return mean/(len(l)-compteNumberOfMiss(l))
    else :
        return -1


def count_comon_element(list1,list2) :
    result = []
    for element in list1:
        if element in list2:
            result.append(element)
    return len(result)

if __name__ == '__main__':
    '''
    This script has been written to optimize the coefficient of our graph algorithms running on neo4j
    If you pass the argument :
        -find_best_doc_tf(query,coeff_1,coeff_2)[0] you'll get the best coefficient for tfidf algorithm
        -find_best_doc_page_rank(query,recall_at, coeff_1, coeff_2) you will get the best coefficient for
        pagerank algorithms
    '''

    # Constants
    recall_at = 10
    count = 0
    neo4j_tf = False
    neo4j_pr = True
    l_score =[]
    l_coefficient = []
    number_of_question = 100 # number of duplicat questions used to find the best coefficients

    # Path to the duplicate questions
    path_to_duplicate = '../Data/duplicate_questions.csv'

    # Load the duplicate questions
    df = pd.read_csv(path_to_duplicate)

    list_pd = []

    for coeff_1 in [0] :

        for coeff_2 in [1] :
            count = 0
            for index, row in df.iterrows():
                count +=1
                print('question number :', count)


                if count == number_of_question :
                    break


                question_uid = row['uid']
                question_title = eval(row['question'])['question_body'] + eval(row['question'])['question_title']

                theoritical_id_list = row['duplicate uid']

                # We query the title of the question
                query = question_title


                if neo4j_tf:
                    print('coefficent question_title_mutiplier', coeff_1)
                    print('coefficent question_body_mutiplier', coeff_2)
                    results_tf = find_best_doc_tf(query,question_title_mutiplier=coeff_1,question_body_mutiplier = coeff_2)[0]
                    results_tf= results_tf[0:recall_at-1]

                    common_element_term_frequency = count_comon_element(results_tf, theoritical_id_list)
                    print('number of matches TF', common_element_term_frequency)
                    common_element_pr = 0

                if neo4j_pr :
                    print('coefficent coefficientAuthor', coeff_1)
                    print('coefficent coefficientWord', coeff_2)
                    results_pr = find_best_doc_page_rank(query, recall_at, coefficientAuthor= coeff_1, coefficientWord=coeff_2)
                    results_pr = results_pr[0:recall_at-1]

                    common_element_pr = count_comon_element(results_pr, theoritical_id_list)
                    print('number of matches PR', common_element_pr)
                    common_element_term_frequency = 0

                list_pd.append([common_element_term_frequency,common_element_pr,coeff_1,coeff_2])

    df = pd.DataFrame(list_pd, columns=['nbr TF', 'nbr PR','Coeff 1','Coeff 2'])

    df.to_csv('optimization_coefficents_tf_local.csv')


