### Thanks a lot to hermidave for its usefull textfile https://github.com/hermitdave/FrequencyWords/


import pandas as pd
from stemming.porter2 import stem

# Generate a csv file containing the frequency of each word : this file can be used to have more accurate models

df = pd.read_csv('en_full.txt', header=None, delimiter=r"\s+")
df.columns = ['WORD' , 'FREQUENCY']
l = []
for e in df['WORD']:
    l.append(stem(str(e)))

df['STEMMED_WORDS'] = pd.DataFrame(l)

df=df.drop_duplicates(['STEMMED_WORDS'],keep = 'first')
df[['STEMMED_WORDS','FREQUENCY']].to_csv('processed_term_frequency.csv')