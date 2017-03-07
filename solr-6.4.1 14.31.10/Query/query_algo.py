import nltk
import  sys
sys.path.append('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10')
from solr_query import SolrQuery
from solr_query import and_
from solr_query import or_
from nltk.corpus import stopwords
import string


def baselineQuery(question,solquery) :
    '''

    :param question: the question you would like to ask
    :param solquery: the solquery object
    :return: the solr response :
        if there is an exact match it return the match
        if not the solr response if built using or
    '''


    # are there perfect match ?

    solquery.set_query(and_('question.question_title:' + question))
    solquery.add_field('id')
    solrResponse = solquery.execute().get_results()



    ## No perfect match
    # if solrResponse == [] :
    if True :
        print(' Perfect Match no found :( ')
        exclude = set(string.punctuation)
        question_without_punctuation = ''.join(ch for ch in question if ch not in exclude)

        stop = set(stopwords.words('english'))

        tokens = []
        for i in question_without_punctuation.lower().split() :
            if i not in stop :
                tokens.append(i)
        Qquery = []
        Aquery = []
        for word in tokens :
            Qquery.append( 'question.question_title:'+word)
            Aquery.append( 'answer.answer_body:'+word)


        questionQuery = '('+' OR '.join(Qquery)+')'
        print(questionQuery)
        answerQuery = '('+' OR '.join(Aquery)+')'
        orQuery = or_(questionQuery,answerQuery)
        productQuery = 'product:'+'outlook'


        solquery.add_field('id')
        solquery.set_query(and_(orQuery,productQuery))


        solrResponse = solquery.execute().get_results()

    return solrResponse


#print('results areeee _____', baselineQuery('coucou comment ca va ?', SolrQuery('localhost:'+'8983', 'ProductDB')))