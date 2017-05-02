#################################################
#  Author : Pierre COLOMBO                      #
#  Name : create_test_validation_....py         #
#                                               #
#  This script has been written to generate the #
#  files to train the RNN on a special data set #
#################################################

import pandas as pd
import json
import random


if __name__ =='main' :

    # Constants :

    path_data_set = 'superuser.com_questions_tagged_ubuntu_items.json'
    path_train_output_directory = 'scripts/superuser/train.csv'
    path_test_output_directory = 'scripts/superuser/test.csv'
    path_valid_output_directory = 'scripts/superuser/valid.csv'

    ratio_test_valid = 0.1

    #################################################################
    ################### Create Test and Valid set ###################
    #################################################################

    print('Create Test and Valid set')
    l_question_body = []
    l_question_title = []

    # Open the json and store the title and the body of the question
    with open(path_data_set) as f:
        data = pd.DataFrame(json.loads(line) for line in f)

    for e in data['question'] :
        l_question_title.append(e['question_title'])
        l_question_body.append(e['question_body'])

    # Assign corresponding question body and question title pairs
    data['Ground Truth Utterance']=l_question_body
    data['Context']=l_question_title

    # Create Distrators : Take random question titles and assign them to body questions
    for j in range(10):
        column_name = 'Distractor_'+ str(j)
        l_distractor = []
        for i in range(data.shape[0]):
            number = int(random.random()*data.shape[0])
            l_distractor.append(data['Ground Truth Utterance'].iloc[number])
        data[column_name] = l_distractor

    # Store test and train sets
    data[['Context','Ground Truth Utterance','Distractor_0','Distractor_1','Distractor_2','Distractor_3','Distractor_4','Distractor_5','Distractor_6',
    'Distractor_7','Distractor_8','Distractor_9'
    ]].iloc[:int(data.shape[0]*ratio_test_valid)].to_csv(path_test_output_directory,index=False)

    data[['Distractor_0','Distractor_1','Distractor_2','Distractor_3','Distractor_4','Distractor_5','Distractor_6',
    'Distractor_7','Distractor_8','Distractor_9','Ground Truth Utterance','Context'
    ]].iloc[int(data.shape[0]*ratio_test_valid):].to_csv(path_valid_output_directory,index=False)



    ########################################################
    ################### Create Train Set ###################
    ########################################################

    print('Create Train Set')
    l_question_title = []
    l_question_body = []


    # Open the json and store the title and the body of the question
    with open(path_data_set) as f:
        data = pd.DataFrame(json.loads(line) for line in f)
    for e in data['question'] :
        l_question_title.append(e['question_title'])
        l_question_body.append(e['question_body'])

    # Assign corresponding question body and question title pairs
    data['Ground Truth Utterance']=l_question_body
    data['Context']=l_question_title
    data['Label'] = 1


    list_context =[]
    list_utterance = []
    list_label =[]
    for i in range(data.shape[0]):
        number = int(random.random() * data.shape[0])
        list_context.append(data['Context'].iloc[number])
        list_utterance.append(data['Ground Truth Utterance'].iloc[number])
        list_label.append(0)

    trainData = pd.DataFrame()
    trainData['Ground Truth Utterance']=list_utterance
    trainData['Context']=list_context
    trainData['Label'] = list_label

    result = pd.concat([trainData,data[['Context','Ground Truth Utterance','Label']]])

    #### mixe for randomless
    result =result.sample(frac=1).reset_index(drop=True)
    result.to_csv(path_train_output_directory,index=False)
