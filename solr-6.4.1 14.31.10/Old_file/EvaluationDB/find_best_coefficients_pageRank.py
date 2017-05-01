import os
import pandas as pd
import sys
import numpy as np
sys.path.append('/Users/pierrecolombo/Documents/knowledge-base/Neo4j/')
from baseline_model import find_best_doc_page_rank,find_best_doc_tf

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
    frecall_neo4j = []
    neo4j = True
    l_score =[]
    l_coefficient = []
    number_of_question = 100 # number of duplicat questions used to find the best coefficients

    # Path to the duplicate questions
    path_to_duplicate = 'evaluationWithOnlyDuplicate.csv'

    # Load the duplicate questions
    df = pd.read_csv(path_to_duplicate)

    for coeff_1 in [0.1,1,50,100,1000] :

        for coeff_2 in [0.1,1,50,100,1000] :
            count = 0
            for index, row in df.iterrows():
                count +=1

                if count == number_of_question :
                    break
                original_url = eval(row['question'])['question_original_url']
                question_uid = row['uid']
                question_title = eval(row['question'])['question_body'] + eval(row['question'])['question_title']

                # We query the title of the question
                query = question_title

                if neo4j:
                    #results = find_best_doc_page_rank(query,recall_at, coeff_1, coeff_2)
                    results = find_best_doc_tf(query,coeff_1,coeff_2)[0]
                    print(results)
                    noe4j_candidates = pd.DataFrame(results)
                    try :
                        noe4j_candidates.columns = ['uid']

                    except ValueError :
                        pass

                    ## Load the expected uid
                    text_file = open(str(os.getcwd()) + '/Output_duplicat/TEXT/' + question_uid +'.csv')
                    lines = text_file.readlines()

                    rank_first_match_neo4j = []
                    number_uid =len(lines)
                    if lines != []:

                        ## Remove uid of the question
                        lines.remove(question_uid + '\n')

                        for i in range(len(lines)):
                            ref_uid = lines[i].rstrip()

                            # Neo4j
                            rank_first_match_neo4j.append(find_first_match(noe4j_candidates, ref_uid, recall_at))

                        try:
                            recall_neo4j = compute_recall(rank_first_match_neo4j, number_uid, recall_at)
                        except ValueError:
                            recall_neo4j = recall_at + 1

                        frecall_neo4j.append(recall_neo4j)

                print('question number',count)



        l_score.append(mean(frecall_neo4j))
        l_coefficient.append((coeff_1,coeff_2))

    ind = np.argmax(l_score)
    print('liste score is ',l_score)
    print('liste coefficeint is ', l_coefficient)
    print('best coefficient',l_coefficient[ind])

