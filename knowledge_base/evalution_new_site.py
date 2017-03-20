import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

import requests
from urllib.parse import urlparse
import os.path

from is_result_page import get_html


#-------------------------------------------------------------------------------
# Script testing if we get good results on the new database site_evalutation.csv:
#---------------------------------------------------------------------------------


if __name__ == "__main__":

    # Paths to the relevant folders
    dir_path = 'fastText/'
    test_path = dir_path + 'cross_validation_data/test_data' + 'newSites'+ '.csv'
    test_labels_path = dir_path + 'cross_validation_data/test_label' + 'newSites' + '.txt'
    model_path = dir_path + 'cross_validation_data/train_model_' + '2'
    test_predictions_path = dir_path +  'cross_validation_data/finalPredicions' + '.txt'


    # Load data and fit it to the right format
    y_te = pd.read_csv(filepath_or_buffer='site_evaluation.csv', delimiter=',')
    y_te.columns = ['link', 'isResultPage']
    content = []
    for link in y_te['link'] :
        content.append(get_html(link))
    y_te['content'] =content

    # Store everything in the right folder

    y_te['isResultPage'].replace(to_replace='Yes', value='__label__Yes ', inplace=True)

    y_te['isResultPage'].replace(to_replace='No', value='__label__No ', inplace=True)

    y_te['content'].to_csv(test_path, index=False)
    print("shape is : ", y_te.shape)
    y_te = y_te[y_te['content'] != 'nan']
    y_te.dropna(axis=0,inplace  = True)
    print("shape is after na : ", y_te.shape)
    y_te['isResultPage'].to_csv(test_labels_path, index=False)

    # Use fast text command
    eval_command = 'fastText/fasttext predict {}.bin {} > {}'.format(model_path, test_path,test_predictions_path)
    os.system(eval_command)
    print('evaluated model')

    with open(test_predictions_path) as f:
        predictions = f.readlines()
        print('prediction is :', predictions)
    with open(test_labels_path) as f:
        correct_labels = f.readlines()
        print('corret_labels is ', correct_labels)

    total = 0
    for label1, label2 in zip(predictions, correct_labels):

        # print('label 1',label1.replace('\n', "").replace(" ", ""))
        # print('label 2',label2.replace('\n', "").replace(" ", ""))
        if label1.replace('\n', "").replace(" ", "") == label2.replace('\n', "").replace(" ", ""):
            total += 1
    accuracy = float(total) / float(len(predictions))
    print('accuracy for fold {} is {}'.format(2, accuracy))


