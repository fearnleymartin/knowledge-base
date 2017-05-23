import fasttext
import pandas as pd

import random

def decision(probability):
    return random.random() < probability


def set_positiv_to_rigth_format(path_input, path_output, pos_prefix,) :

    df = pd.read_json(path_input,lines = True)
    l_label = []
    l_text = []

    for index, row in df.iterrows():

        text = row['answer']['answer_body']
        text = text.replace("\n", "")
        if decision(0.5) :
            l_label.append('__label__POS')
        else :
            l_label.append('__label__NEG')
        l_text.append(' ' + text)

    final_data = pd.DataFrame(l_text,l_label)
    print(final_data.head())
    final_data.to_csv(path_output,header = False)




if __name__ == '__main__' :
    set_positiv_to_rigth_format('solr/Old_file/Data/test.json','coucou.txt','__label__')

    ## Train fast text :
    classifier = fasttext.supervised('coucou.txt', 'model', label_prefix='__label__',
                                     thread=12,epoch  = 20,lr  = 0.01)

    ## Load text to evaluate :
    texts = ['example vefin fpomamnf neifo','coucou mon cher !']
    labels = classifier.predict(texts)
    print(labels)