#################################################
#  Author : Pierre COLOMBO                      #
#  Name : pipeline_to_evaluate.py               #
#                                               #
#  This script has been written to generate the #
#  evaluation files you need to run the notebook#
#################################################

import sys
import numpy as np
import tensorflow as tf
import pandas as pd
from nltk.corpus import stopwords

import solr.chatbotInformationRetrieval.udc_model
import solr.chatbotInformationRetrieval.udc_hparams

import json
import string

from Neo4j.baseline_model import find_best_doc_page_rank,find_best_doc_tf

from solr.chatbotInformationRetrieval.models.dual_encoder import dual_encoder_model
import requests





def tokenizer_fn(iterator):
    '''

    :param iterator:
    :return: The tokenized query
    '''
    return (x.split(" ") for x in iterator)



def get_features(context, utterance,vp):
  context_matrix = np.array(list(vp.transform([context])))
  utterance_matrix = np.array(list(vp.transform([utterance])))
  context_len = len(context.split(" "))
  utterance_len = len(utterance.split(" "))
  features = {
    "context": tf.convert_to_tensor(context_matrix, dtype=tf.int64),
    "context_len": tf.constant(context_len, shape=[1,1], dtype=tf.int64),
    "utterance": tf.convert_to_tensor(utterance_matrix, dtype=tf.int64),
    "utterance_len": tf.constant(utterance_len, shape=[1,1], dtype=tf.int64),
  }
  return features, None


def filter_raw_query(raw_query) :
    '''

    :param raw_query: The unfiltered query
    :return: Query without punction  and stop words
    '''
    filtered_words = [word for word in raw_query.split() if word not in stopwords.words('english')]
    raw_query = ''
    for word in filtered_words :
        raw_query += ' ' + word

    raw_query.translate(string.punctuation)

    return raw_query.replace(" ", "+")



def predict_save_solr_results(raw_query , model_dir = "runs/1491654958", vocab_processor_file = "scripts/" + "mydata/vocab_processor.bin",
                number_results = 100,solr_server = 'http://localhost:8983/solr/',col_name = 'Evaluation/',
                              uid_question = 0, recall_at_k =10, baseline=True , rnn =True,
                              path_rnn =  '../Old_file/EvaluationDB/Output_duplicat/RNN/',
                              path_solr ='../Old_file/EvaluationDB/Output_duplicat/BASELINE/', save = True) :
    '''

    This function query solr and create 3 files :
        - one file with the results provided by solr
        - one file with the results reranked by the rnn
        - one file with the theoritical ids i.e the ideas of all duplicated questions

    :param raw_query: The unfiltered query you want to perform
    :param model_dir: Path where the run are saved
    :param vocab_processor_file: Path where the vocabulary is stored
    :param number_results: The number of results you want that the rnn rerank
    :param solr_server: The adress of the solr server
    :param col_name: The core name
    :param uid_question:
    :param recall_at_k: The k best results you want to store
    :return: void
    '''
    try :

      # Define query and URL
      query = filter_raw_query(raw_query)
      #product = __get__product_name(query)
      url_query = solr_server + col_name + 'select?q=' + query \
                  + '&defType=edismax&qf=question.question_body^1+question.question_title^1' \
                  + '&rows='+ str(number_results) \
                  + '&fl=*,score' + '&wt=json'
      r = requests.get(url_query).json()


      # Candidate returned by solr
      candidates_objects = r['response']['docs']

      candidates = [c['question.question_body'] for c in candidates_objects]
      candidates_uid = [c['uid'] for c in candidates_objects]

      # Load vocabulary
      vp = tf.contrib.learn.preprocessing.VocabularyProcessor.restore(
        vocab_processor_file)

      # Load your own data here
      INPUT_CONTEXT = query
      POTENTIAL_RESPONSES = candidates

      # Do the prediction
      hparams = udc_hparams.create_hparams()
      model_fn = udc_model.create_model_fn(hparams, model_impl=dual_encoder_model)
      estimator = tf.contrib.learn.Estimator(model_fn=model_fn, model_dir=model_dir)
      estimator._targets_info = tf.contrib.learn.estimators.tensor_signature.TensorSignature(tf.constant(0, shape=[1,1]))
      scores = []


      for r in POTENTIAL_RESPONSES:
        prob = estimator.predict(input_fn=lambda: get_features(INPUT_CONTEXT, r,vp))
        results = prob[0][0]
        scores.append(results)

      num_candidates = sorted(range(len(scores)), key=lambda i: scores[i])[-recall_at_k:][::-1]
      uid_candidate = []


    # SAVE RNN CANDIDATES
      if rnn :
              for i in range(recall_at_k) :
                  uid_candidate.append(candidates_uid[num_candidates[i]])
              save_dataframe(uid_candidate,path_rnn,'uid',uid_question)

          #SAVE BASELINE PREDICTION
      if baseline :
            save_dataframe(candidates_uid, path_solr, 'uid', uid_question )




    except json.decoder.JSONDecodeError :
      print('ERROR')

    except KeyError :
      print('ERROR')



def front_end_prediction(Inputquery, number_of_result ) :
    '''
    This function is the one called in the front end
    :param Inputquery: the query asked by the user
    :param number_of_result: The number of results you would like to display
    :return:  noe4j_response,rnn_response,solr_response
    '''
    solr_server = 'http://localhost:8983/solr/'
    col_name = 'Evaluation/'


    ############################
    ###### Get Solr_answer ######
    ############################

    query = filter_raw_query(Inputquery)
    # product = __get__product_name(query)
    url_query = solr_server + col_name + 'select?q=' + query \
                + '&defType=edismax&qf=question.question_body^1+question.question_title^1' \
                + '&rows=' + str(number_of_result) \
                + '&fl=*,score' + '&wt=json'
    r = requests.get(url_query).json()
    candidates_objects = r['response']['docs']


    solr_response = []
    for element in candidates_objects:
        ### check the field title if it is exactly the same do not add
        solr_response.append(element['answer.answer_body'])



    ############################
    ###### Get RNN_answer ######
    ############################


    model_dir = "runs/1494252297"
    vocab_processor_file = "scripts/" + "super_user_big_dataset/vocab_processor.bin"

    candidates = [c['question.question_body'] for c in candidates_objects]
    candidates_uid = [c['uid'] for c in candidates_objects]

    # Load vocabulary
    vp = tf.contrib.learn.preprocessing.VocabularyProcessor.restore(
        vocab_processor_file)

      # Load your own data here
    INPUT_CONTEXT = Inputquery
    POTENTIAL_RESPONSES = candidates

    # Do the prediction
    hparams = udc_hparams.create_hparams()
    model_fn = udc_model.create_model_fn(hparams, model_impl=dual_encoder_model)
    estimator = tf.contrib.learn.Estimator(model_fn=model_fn, model_dir=model_dir)
    estimator._targets_info = tf.contrib.learn.estimators.tensor_signature.TensorSignature(tf.constant(0, shape=[1,1]))
    scores = []

    for r in POTENTIAL_RESPONSES:
        prob = estimator.predict(input_fn=lambda: get_features(INPUT_CONTEXT, r,vp))
        results = prob[0][0]
        scores.append(results)

    num_candidates = sorted(range(len(scores)), key=lambda i: scores[i])[-100:][::-1]
    uid_candidate = []


    # Query solr to get answers #

    for i in range(number_of_result) :
        uid_candidate.append(candidates_uid[num_candidates[i]])

    for id in uid_candidate :
        url_query = solr_server + col_name + 'select?q=' + str(id) \
                    + '&defType=edismax&qf=uid' \
                    + '&rows=' + str(1) \
                    + '&fl=*,score' + '&wt=json'
        r = requests.get(url_query).json()
        candidates_objects = r['response']['docs']

        rnn_response = []
        for element in candidates_objects:
            ### check the field title if it is exactly the same do not add
            rnn_response.append(element['answer.answer_body'])



    ############################
    ###### Get Neo4j_answer ######
    ############################

    results_neo4j = find_best_doc_tf(Inputquery, 1, 1)[0]


    # Query solr to get answers #
    for id in results_neo4j :
        url_query = solr_server + col_name + 'select?q=' + str(id) \
                    + '&defType=edismax&qf=uid' \
                    + '&rows=' + str(1) \
                    + '&fl=*,score' + '&wt=json'
        r = requests.get(url_query).json()
        candidates_objects = r['response']['docs']

        noe4j_response = []
        for element in candidates_objects:
            ### check the field title if it is exactly the same do not add
            noe4j_response.append(element['answer.answer_body'])


    return noe4j_response,rnn_response,solr_response






def save_dataframe(uid_candidate ,path = '../Old_file/EvaluationDB/Output_duplicat/RNN/' ,column_name = 'uid',uid_question= ''):
    '''
    This function saved datframe used to factor a bit the code

    :param uid_candidate: the uid of the best candidates
    :param path: where you want to store the files
    :param column_name: uid
    :param uid_question: the uid of the question you use to perform your query
    :return:
    '''
    nn_candidates = pd.DataFrame(uid_candidate)
    nn_candidates.columns = [column_name]
    predict_dir = path + uid_question + '.csv'
    nn_candidates.to_csv(path_or_buf=predict_dir)



def create_Theoritical_id(path,uid_question, all_id):
    '''
    This functino save the duplicats id

    :param path: where you want to store the files
    :param uid_question:
    :param all_id:
    :return:
    '''
    with open(path+ uid_question + ".csv", "w") as text_file:
        text_file.writelines(["%s\n" % item for item in all_id])

def create_uid_list_of_duplicat(solr_server,col_name,number_results,original_url) :
    '''

    :param solr_server: the solr server adress
    :param col_name: core name
    :param number_results: number of results you want
    :param original_url: the url of your original question
    :return: a containing the uuid of all duplicated questions
    '''
    uid_list = []
    complete_list = list(original_url)
    while original_url != []:

        url = original_url[0]
        if url not in complete_list:
            complete_list.append(url)

        url_query = solr_server + col_name + 'select?q=' + url + '&defType=edismax&qf=question.question_original_url' + '&rows=' + str(
            number_results) + '&fl=*,score' + '&wt=json'
        r = requests.get(url_query).json()
        candidates_objects = r['response']['docs']

        for element in candidates_objects:
            ### check the field title if it is exactly the same do not add
            uid_list.append(element['uid'])
            for newUrl in element['question.question_original_url']:
                if newUrl not in complete_list:
                    original_url.append(newUrl)

        original_url.remove(url)

    uid_list = list(set(uid_list))
    return uid_list


def main():
    front_end_prediction('outlook crashed', 10)

    '''

    # Solr parameters :
    solr_server = 'http://localhost:8983/solr/'
    col_name = 'Evaluation/'
    number_results = 100
    recall_at_k = 10

    # RNN parameters :
    model_dir = "runs/1493320213"  # 1493320213 # ubuntu 1490608921
    vocab_processor_file = "scripts/" + "superuser/vocab_processor.bin" # data #superuser

    # Decide what model you want to predict :
    baseline = False
    rnn = False
    theoretical_id = False
    neo4j = True

    # Path to the duplicate questions
    path_to_duplicate = '../Old_file/EvaluationDB/evaluationWithOnlyDuplicate.csv'

    # Path for saving predictions
    path_rnn = '../Old_file/EvaluationDB/Output_duplicat/RNN200/'
    path_solr = '../Old_file/EvaluationDB/Output_duplicat/BASELINE/'


    # Load the duplicate questions
    df = pd.read_csv(path_to_duplicate)


    count = 0
    for index, row in df.iterrows() :
        count  +=1
        print('Question duplicat number : ---------------', count)

        original_url=eval(row['question'])['question_original_url']
        question_uid = row['uid']
        question_title=eval(row['question'])['question_body'] + eval(row['question'])['question_title']


        uid_list = create_uid_list_of_duplicat(solr_server,col_name,number_results,original_url)


        # THEORITICAL IDS
        if theoretical_id :
            create_Theoritical_id("../Old_file/EvaluationDB/Output_duplicat/TEXT/", question_uid, uid_list)

        # We query the title of the question
        query = question_title

        # Create BASELINE + RNN + Theoritical ID
        if baseline or rnn :
            predict_save_solr_results(query , model_dir,vocab_processor_file,number_results,solr_server,col_name ,
                                  question_uid,recall_at_k, baseline ,rnn, path_rnn,path_solr)



        if neo4j:
            results = find_best_doc_tf(query,1,1)[0]
            print(results)
            noe4j_candidates = pd.DataFrame(results)
            try :
                noe4j_candidates.columns = ['uid']
                predict_dir = '../Old_file/EvaluationDB/Output_duplicat/NEO4J/' + question_uid + '.csv'
                noe4j_candidates.to_csv(path_or_buf=predict_dir)
            except ValueError :
                pass

    '''
main()
