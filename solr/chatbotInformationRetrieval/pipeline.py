import os
import time
import itertools
import sys
import numpy as np
import tensorflow as tf
import pandas as pd

import solr.chatbotInformationRetrieval.udc_model
import solr.chatbotInformationRetrieval.udc_hparams
import solr.chatbotInformationRetrieval.udc_metrics
import solr.chatbotInformationRetrieval.udc_inputs

from solr.chatbotInformationRetrieval.models.dual_encoder import dual_encoder_model
from solr.chatbotInformationRetrieval.models.helpers import load_vocab
import requests


from solr.Query.query_algo import __get__product_name, baselineQuery


def tokenizer_fn(iterator):
  return (x.split(" ") for x in iterator)



def get_features(context, utterance):
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




tf.flags.DEFINE_string("raw_query", 'outlook takes too long load how can make faster', "Question that must be answered")
tf.flags.DEFINE_string("model_dir", "runs/1490608921", "Directory to load model checkpoints from")
tf.flags.DEFINE_string("vocab_processor_file", "scripts/" + "data/vocab_processor.bin", "Saved vocabulary processor file")

FLAGS = tf.flags.FLAGS

if not FLAGS.model_dir:
  print("You must specify a model directory")
  sys.exit(1)

if not FLAGS.raw_query:
  print("You must ask a question!")
  sys.exit(1)
solr_server = 'http://localhost:8983/solr/'

#col_name = 'Evaluation/'
col_name = 'Evaluation/'
raw_query = FLAGS.raw_query
query = raw_query.replace(" ", "+")
#print('query is : ',str(query))
number_results = 100
product = __get__product_name(raw_query)

if True : #product == '' :
    url_query = solr_server + col_name + 'select?q=' + query + '&defType=edismax&qf=question.question_body^1+question.question_title^1'+ '&rows=' + str(
        number_results) +'&fl=*,score'+'&wt=json'
else :
    url_query = solr_server + col_name + 'select?q='+query +'&defType=edismax&qf=question.question_body^1+question.question_title^1&bq=product:'+product +'^5.0'+ '&rows=' + str(number_results)+'&fl=*,score' + '&wt=json'
#url_query = solr_server + col_name + 'select?defType=edismax&indent=on&bq=question.question_body:[*%20TO%20*]^5&q.alt=' + query + '&qf=question.question_body&rows=' + str(number_results) + '&wt=json'
print(url_query)

r = requests.get(url_query).json()

candidates_objects = r['response']['docs']
print(candidates_objects)
candidates = [ c['answer.answer_body'] for c in candidates_objects ]

candidates_question_title = [ c['question.question_title'] for c in candidates_objects ]
candidates_question_body = [ c['question.question_body'] for c in candidates_objects ]
candidates_product = [ c['product'] for c in candidates_objects ]
####candidates_type = [ c['breakdown'] for c in candidates_objects ]
#print('candidates are : ',candidates)

# Load vocabulary
vp = tf.contrib.learn.preprocessing.VocabularyProcessor.restore(
  FLAGS.vocab_processor_file)

# Load your own data here
INPUT_CONTEXT = raw_query
POTENTIAL_RESPONSES = candidates


if __name__ == '__main__':
  hparams = udc_hparams.create_hparams()
  model_fn = udc_model.create_model_fn(hparams, model_impl=dual_encoder_model)
  estimator = tf.contrib.learn.Estimator(model_fn=model_fn, model_dir=FLAGS.model_dir)

  # Ugly hack, seems to be a bug in Tensorflow
  # estimator.predict doesn't work without this line
  estimator._targets_info = tf.contrib.learn.estimators.tensor_signature.TensorSignature(tf.constant(0, shape=[1,1]))

  print("Context: {}".format(INPUT_CONTEXT))
  scores = []
  highest = 0
  final_answer = 'I do not understand. Can you please ask another question?'
  position = 0
  for r in POTENTIAL_RESPONSES:
    prob = estimator.predict(input_fn=lambda: get_features(INPUT_CONTEXT, r))
    results = prob[0][0]
    scores.append(results)

  number = 5
  num_candidates = sorted(range(len(scores)), key=lambda i: scores[i])[-number:][::-1]
  print(num_candidates)
  response_candidates = []
  question_title_candidates = []
  question_body_candidates = []
  type_candidate = []
  product_candidate = []
  body_candidate = []


  ##### Neural NET CANDIDATES
  for i in range(number) :
      body_candidate.append(candidates[num_candidates[i]])
      question_title_candidates.append(candidates_question_title[num_candidates[i]])
      question_body_candidates.append(candidates_question_body[num_candidates[i]])
      response_candidates.append(POTENTIAL_RESPONSES[num_candidates[i]])
      ####type_candidate.append(candidates_type[num_candidates[i]])
      product_candidate.append(candidates_product[num_candidates[i]])


  nn_candidates=pd.DataFrame(body_candidate)
  nn_candidates.columns = ['answer_body']
  nn_candidates['question_body'] = pd.DataFrame(question_body_candidates)
  nn_candidates['question_title'] = pd.DataFrame(question_title_candidates)
  nn_candidates['product'] = pd.DataFrame(product_candidate)
  #####nn_candidates['type'] = pd.DataFrame(type_candidate)
  print(nn_candidates.head())
  predict_dir = '../Old_file/EvaluationDB/' + 'answers_nn.csv'
  nn_candidates.to_csv(path_or_buf=predict_dir)



  ###### BASELINE

  solr_candidates = pd.DataFrame(candidates)
  solr_candidates.columns = ['answer_body']
  solr_candidates['question_body'] = pd.DataFrame(candidates_question_body)
  solr_candidates['question_title'] = pd.DataFrame(candidates_question_title)
  solr_candidates['product'] = pd.DataFrame(candidates_product)
  #####solr_candidates['type'] = pd.DataFrame(candidates_type)
  predict_dir = '../Old_file/EvaluationDB/' + 'answers_solr.csv'
  solr_candidates.to_csv(path_or_buf=predict_dir)


  ###### SOLR BASELINE :
  baseLine = baselineQuery(raw_query)
  df = pd.DataFrame(baseLine[:number])
  predict_dir = '../Old_file/EvaluationDB/' + 'answers_baseline.csv'
  df.to_csv(path_or_buf=predict_dir)

   ####### Geometric mean
