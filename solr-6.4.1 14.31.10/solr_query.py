import hashlib
import json
import logging
import urllib
from urllib.parse import urljoin
from collections import OrderedDict
from datetime import date, datetime, timezone
from urllib.request import urlopen
from requests import Session, Request
import os
import sys

logger = logging.getLogger(__name__)


class SolrException(Exception):
    pass


'''
Below there is a bunch of kinda static functions that you can (must?) use to create Solr queries
'''


def and_(*args):
    """
    Build an AND query
    :param args: a list of Solr queries, normally built with match_, exact_match_, from_to_, etc.
    :return: the AND query - a string having all the queries in args separated by an AND
    """
    return __format_params__('({})', ' AND '.join(args))


def or_(*args):
    """
    Build an OR query
    :param args: a list of Solr queries, normally built with match_, exact_match_, from_to_, etc.
    :return: the OR query - a string having all the queries in args separated by an OR
    """
    return __format_params__('({})', ' OR '.join(args))


def from_to_(field, from_, to_):
    """
    Build a from to query: e.g. 'field:[a TO b]'
    :param field: the field name
    :param from_: the initial value
    :param to_: the end value
    :return: the built query
    """
    return __format_params__('({}:[{} TO {}])', field, from_, to_)


def from_(field, from_):
    """
    Build a from query: e.g. 'field:[a TO *]'
    :param field: the field name
    :param from_: the initial value
    :return: the built query
    """
    return from_to_(field, from_, '*')


def to_(field, to_):
    """
    Build a to query: e.g. 'field:[* TO b]'
    :param field: the field name
    :param to_: the end value
    :return: the built query
    """
    return from_to_(field, '*', to_)


def exact_match_(field, value):
    """
    Build an exact match query: e.g. 'field:"value"'
    :param field: the field name
    :param value: the value to be exactly matched
    :return: the built query
    """
    return __format_params__('({}:"{}")', field, value)


def match_(field, value):
    """
    Build a match query: e.g. 'field:value'
    :param field: the field name
    :param value: the value to be matched
    :return: the built query
    """
    return __format_params__('({}:({}))', field, value)


def facet_(*args):
    """
    Build the aggregation in the faceted queries
    :param args: tuples of names and values of the field you want to aggregate. Use sum_ or avg_ like in tests
    :return: the ordered dictionary to pass to the add_range_faceting or add_term_faceting methods
    """
    facet = OrderedDict()
    for arg in args:
        alias, value = arg
        facet[alias] = value
    return facet


def desc_(field=None):
    """
    Helps to sort results, either in normal Solr query or in terms faceted search
    :param field: the name of the field you want to order by desc. If not filled just returns the string 'desc' used
    for terms faceting sorting -- see the tests for an example
    :return: the field plus the 'desc'
    """
    if field:
        return __format_params__('{} desc', field)
    else:
        return 'desc'


def asc_(field=None):
    """
    Helps to sort results, either in normal Solr query or in terms faceted search
    :param field: the name of the field you want to order by desc. If not filled just returns the string 'asc' used
    for terms faceting sorting -- see the tests for an example
    :return: the field plus the 'asc'
    """
    if field:
        return __format_params__('{} asc', field)
    else:
        return 'asc'


def sum_(field):
    """
    Aggregation function for faceting search
    :param field: the name of the field you want to compute the sum.
    :return: the string to pass to the facet_ function
    """
    return __format_params__('sum({})', field)


def avg_(field):
    """
    Aggregation function for faceting search
    :param field: the name of the field you want to compute the average.
    :return: the string to pass to the facet_ function
    """
    return __format_params__('avg({})', field)


class SolrQuery:
    """
    Main class to handle Solr queries
    """
    def __init__(self, solr_server, solr_core):
        self.solr_server = solr_server
        self.solr_core = solr_core
        self.__init_query__()
        self.last_result = None

    def __init_query__(self):
        self.__query_parameters__ = __init_query_parameters__()

    def reset(self):
        """
        Reset all the query parameters
        """
        self.__init_query__()

    def __get_flatten_parameters__(self):
        flatten_params = self.__query_parameters__.copy()
        for parameter, value in flatten_params.items():
            if value is not None:
                if parameter == 'fl':
                    flatten_params['fl'] = ','.join(value)
                elif parameter == 'json.facet':
                    flatten_params['json.facet'] = json.dumps(value, default=__json_default__)
        return flatten_params

    def execute(self):
        """
        Execute the query
        :return: a SolrReponse object
        """
        url = 'http://'+self.solr_server + '/solr/' + str(self.solr_core) + '/select?'
        print(url)

        request = Request('GET', url, params=self.__get_flatten_parameters__(),
                          headers={'accept': 'application/json'}).prepare()

        request_id = hashlib.sha1(bytes(request.url, encoding='UTF-8')).hexdigest()[:5]
        logger.debug("query {id}: url='{url}'".format(id=request_id, url=urllib.parse.unquote(request.url)))

        self.last_result = Session().send(request)
        if self.last_result.status_code == 200:
            return SolrResponse(json.loads(self.last_result.text, object_hook=__json_date_hook__))
        else:
            raise SolrException(self.last_result.text)

    def set_query(self, query):
        """
        Define the query in Solr ('q' parameter). This method should be called only once.
        Every new call will override the previous query.
        :param query: The query as a String, but you should use all the "static" functions like and_, or_, match_,
        exact_match, etc. to build that query
        """
        self.__query_parameters__['fq'] = query

    def add_filter(self, *args):
        """
        Add filters to the query ('fq' parameters). You can add several filters as args or call the method several times
        :param args: One or several filters. Again you should use match_, exact_match_, from_, etc. to build the filters
        """
        if self.__query_parameters__['fq'] is not None:
            for arg in args:
                self.__query_parameters__['fq'].add(arg)
        else:
            self.__query_parameters__['fq'] = set(args)

    def add_field(self, *args):
        """
        Restrain the fields that Solr outputs in the results ('fl' parameter).
        You can add several fields in a call or call the method several times
        :param args: One or several field names.
        """
        if self.__query_parameters__['fl'] is not None:
            for arg in args:
                self.__query_parameters__['fl'].add(arg)
        else:
            self.__query_parameters__['fl'] = set(args)

    def set_rows(self, rows):
        """
        Defines the number of rows you want Solr to return ('rows' parameter)
        :param rows: A number - defaulted to 10 in Solr.
        """
        self.__query_parameters__['rows'] = rows

    def set_start(self, start):
        """
        Defines the start of the douments in the results ('start' parameter).
        Used for pagination (e.g. rows=20 and start=40 will give you the third page with 20 documents per page)
        :param start: A number - defaulted to 0 in Solr.
        """
        self.__query_parameters__['start'] = start

    def set_sort(self, *args):
        """
        Defines the way the documents should be sorted by Solr ('sort' parameter)
        :param args: A list of field names plus their order as a String.
        But you should use the "static" functions desc_ and asc_ to create these.
        """
        self.__query_parameters__['sort'] = ','.join(args)


    def clean_DB(self):
        '''
        Deleat all the DB
        :return: VOID
        '''

        if len(sys.argv) > 0:
            os.chdir('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10/')
            req ='curl http://localhost:8983/solr/ProductDB/update?commit=true -d '+'\"<delete><query>*:*</query ></delete>\"'
            print(req)
            os.system(req)
            #os.system('bin/post -c ' + self.solr_core + ' ' +'-d ' +'\"<delete><query>*:*</query ></delete>\"')

        return

    def add_doc(self,path):
        '''
        add a doc to the database
        :param path: doc path you want to add
        :return: void
        '''
        # with open('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10/' + path) as f:
        #     content = f.readlines()
        # # first and last line no ,
        # with open('formatted_file' + '.json', 'w') as outfile:
        #     i = 0
        #     for line in content :
        #         if(i == 0 or i == len(content)-1) :
        #             outfile.write(line )
        #             i +=1
        #         else :
        #             outfile.write(line + ',')
        #             i += 1
        if len(sys.argv) > 0:
            os.chdir('/Users/pierrecolombo/Documents/knowledge-base/solr-6.4.1 14.31.10/')
            print(os.getcwd())
            print('bin/post -c ' + str(self.solr_core)  + ' ' + path)
            os.system('bin/post -c ' + str(self.solr_core)  + ' ' + path)

    def __set_near_query__(self,field_name,keywords,dist,number =10):
        """
        Define the query in Solr ('q' parameter). This method should be called only once.
        Every new call will override the previous query.
        :param query: The query as a String, but you should use all the "static" functions like and_, or_, match_,
        exact_match, etc. to build that query
        """
        self.__query_parameters__['q'] = '*:*'
        self.__query_parameters__['defType'] ='edismax'
        self.__query_parameters__['q.alt'] =keywords
        self.__query_parameters__['qf'] = field_name
        self.__query_parameters__['bq'] = None
        self.__query_parameters__['rows'] = number


def __init_query_parameters__():
    # Initial query parameters. If you just create a SolrQuery object and execute it, it should return everything
    return OrderedDict((
        ('wt', 'json'),
        ('q', '*:*'),
        ('fl', None),
        ('fq', None),
        ('rows', None),
        ('start', None),
        ('sort', None),
        ('defType',None),
        ('q.alt',None),
        ('qf',None),
        ('bq',None)
    )
    )


def __date_to_solr__(datetime_obj):
    # Conversion of datetime or date to the String format Solr expects for dates.
    if isinstance(datetime_obj, datetime):
        return '{0:%Y}-{0:%m}-{0:%d}T{0:%H}:{0:%M}:{0:%S}Z'.format(datetime_obj)
    elif isinstance(datetime_obj, date):
        return '{0:%Y}-{0:%m}-{0:%d}T00:00:00Z'.format(datetime_obj)
    else:
        return datetime_obj


def __json_default__(obj):
    # Json parser for dates to dump them the Solr way
    if isinstance(obj, (datetime, date)):
        return __date_to_solr__(obj)
    raise TypeError('Not sure how to serialize %s' % (obj,))


def __json_date_hook__(json_dict):
    # Json parser for Solr dates to load them into datetime objects
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
    return json_dict


def __format_params__(string_to_format, *args):
    # How to format all params well for Solr
    l_args = list(args)
    for i, arg in enumerate(l_args):
        if isinstance(arg, (datetime, date)):
            l_args[i] = __date_to_solr__(arg)
    return string_to_format.format(*l_args)


class SolrResponse:
    """
    Class to handle Solr reponse
    """
    def __init__(self, json_result):
        """
        Constructor of the classe.
        :param json_result: the json as Solr returns it with the response headers and everything.
        """
        self.__json_result__ = json_result
        if self.__json_result__ and 'response' in self.__json_result__:
            self.__response__ = self.__json_result__['response']
            if 'numFound' in self.__response__:
                self.__nb_documents__ = self.__response__['numFound']
            if 'start' in self.__response__:
                self.__start__ = self.__response__['start']
            if 'docs' in self.__response__:
                self.__results__ = self.__response__['docs']


    def get_json_result(self):
        """
        Normally you will want to use other handlers to not redo the parsing of the results
        :return: the json results (as a dict) as given by Solr with everything (responseHeader also)
        """
        return self.__json_result__

    def get_response(self):
        """
        Normally you will want to use other handlers to not redo the parsing of the results
        :return: the response in the Solr json. Equivalent to get_json_results()['response']
        """
        return self.__response__

    def get_total_nb_results(self):
        """
        :return: the total number of results (not just the ones in get_results())
        """
        return self.__nb_documents__

    def get_start_results_index(self):
        """
        :return: the index of the current result set (for pagination)
        """
        return self.__start__

    def get_results(self):
        """
        :return: the list of results retrieved by the query
        """
        return self.__results__

'''
solquery = SolrQuery('localhost:8983','ProductDB')
solquery.clean_DB()

solquery.add_doc('server/solr/ProductDB/Full.json')

# filter by fiel
#solquery.add_field('question.question_upvotes')

# query specific field
#solquery.set_query('question.question_tags:tag2')
#solquery.set_query('answer.answer_accepted:False')
#solquery.clean_DB()
#solrResponse = solquery.execute()
#print(solrResponse.get_results())



solquery = SolrQuery('localhost:8983','ProductDB')



file = open('research_words','r')
s = file.read()
#solquery.set_query('question.question_title:'+ '\"'+str(s)+'~1'+ '\"')
solquery.__set_near_query__('question.question_title:',str(s),10,10)
print('question.question_title:'+ '\''+str(s)+ '\'')
solquery.add_field('question.question_title')
solrResponse = solquery.execute()
print(solrResponse.get_results())'''


