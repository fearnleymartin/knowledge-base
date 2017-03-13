import nltk
import  sys
sys.path.append('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10')
from solr_query import SolrQuery
from solr_query import and_
from solr_query import or_
from nltk.corpus import stopwords
import string

def __get__product_name(question) :
    '''

    :param question: question we want to query
    :return: the name of the product if it exists
    '''

    for product in question.split() :

        with open('../../Products/Microsoft.txt') as f:
           for line in f:
                # perfect match
                if(line.lower() == product.lower() +'\n'):
                    return product.lower()


        with open('../../Products/Apple.txt') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            for line in content:
                # perfect match
                if(line.lower() == product.lower()):
                    return product.lower()



#print(__get__product_name('coucou je cherche un wdows'))


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
        #print(' Perfect Match no found :( ')
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
            Qquery.append( 'question.question_title:'+ word)
            Aquery.append( 'answer.answer_body:'+ word )


        questionQuery = '('+' OR '.join(Qquery)+')'
        print(questionQuery)
        answerQuery = '('+' OR '.join(Aquery)+')'
        orQuery = or_(questionQuery,answerQuery)

        if (str(__get__product_name(question)) != 'None'):
            productQuery = 'product:'+ str(__get__product_name(question))
            print('The product name is : ',str(__get__product_name(question)))
            solquery.set_query(and_(orQuery, productQuery))
        else :
            print('No product name found')
            solquery.set_query(orQuery)


        solquery.add_field('id')
        solquery.set_rows()



        solrResponse = solquery.execute().get_results()

    return solrResponse


def baseline_near_Query(question,solquery) :
    '''

    :param question: the question you would like to ask
    :param solquery: the solquery object
    :return: the solr response :
        if there is an exact match it return the match
        if not the solr response if built using or

    with near * therms
    '''


    # are there perfect match ?

    solquery.set_query(and_('question.question_title:' + question))
    solquery.add_field('id')
    solrResponse = solquery.execute().get_results()



    ## No perfect match
    # if solrResponse == [] :
    if True :
        #print(' Perfect Match no found :( ')
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
            Qquery.append( 'question.question_title:'+'(' + word + '*)')
            Aquery.append( 'answer.answer_body:'+'(' + word + '*)')


        questionQuery = '('+' OR '.join(Qquery)+')'
        print(questionQuery)
        answerQuery = '('+' OR '.join(Aquery)+')'
        orQuery = or_(questionQuery,answerQuery)

        if (str(__get__product_name(question)) != 'None'):
            productQuery = 'product:'+ str(__get__product_name(question))
            #print('The product name is : ',str(__get__product_name(question)))
            solquery.set_query(and_(orQuery, productQuery))
        else :
            #print('No product name found')
            solquery.set_query(orQuery)


        solquery.add_field('id')
        solquery.set_rows()
        solrResponse = solquery.execute().get_results()

    return solrResponse

## ideas : boost by field it is a beat cheated ^^
## give weigths to each fields


def baseline_near_boosted_Query(question, solquery,question_boost,answer_boost, product_boost):
    '''

    :param question: the question you would like to ask
    :param solquery: the solquery object
    :return: the solr response :
        if there is an exact match it return the match
        if not the solr response if built using or

    with near * therms

    boosted
    '''

    # are there perfect match ?

    solquery.set_query(and_('question.question_title:' + question))
    solquery.add_field('id')
    solrResponse = solquery.execute().get_results()

    ## No perfect match
    # if solrResponse == [] :
    if True:
        #print(' Perfect Match no found :( ')
        exclude = set(string.punctuation)
        question_without_punctuation = ''.join(ch for ch in question if ch not in exclude)

        stop = set(stopwords.words('english'))

        tokens = []
        for i in question_without_punctuation.lower().split():
            if i not in stop:
                tokens.append(i)
        Qquery = []
        Aquery = []
        for word in tokens:
            Qquery.append('question.question_title:' + '(' + word + '*)^'+question_boost)
            Aquery.append('answer.answer_body:' + '(' + word + '*)^'+answer_boost)

        questionQuery = '(' + ' OR '.join(Qquery) + ')'
        print('questionQuery is :',questionQuery)
        print(questionQuery)
        answerQuery = '(' + ' OR '.join(Aquery) + ')'
        orQuery = or_(questionQuery, answerQuery)

        if (str(__get__product_name(question)) != 'None'):
            productQuery = 'product:' + str(__get__product_name(question))
            print('The product name is : ', str(__get__product_name(question)))
            solquery.set_query(and_(orQuery, ''+productQuery+'^'+product_boost))
        else:
            print('No product name found')
            solquery.set_query(orQuery)

        solquery.add_field('id')
        solquery.set_rows()

        solrResponse = solquery.execute().get_results()

    return solrResponse

