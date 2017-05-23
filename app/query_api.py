"""
Micro-service restful api for Q/A queries
"""

from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse

from solr.chatbotInformationRetrieval.pipeline_to_evaluate import front_end_prediction, tokenizer_fn

app = Flask(__name__)
api = Api(app)


class Query(Resource):
    """
	"""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('query', type=str, required=True,
                                   location='json')

    def post(self):
        args = self.reqparse.parse_args()
        query = args['query']
        print('my query is :',query)
        # TODO insert query code here
        # answer = {'solr': solr_query(query),
        # 		   'rnn': rnn_query(query),
        # 		  'neo4j': neo4j_query(query)}
        number_of_answer = 10

        list_answer_neo4j, list_answer_rnn, list_answer_solr = front_end_prediction(query, number_of_answer)

        answer = {'solr': list_answer_solr,
                  'rnn': list_answer_rnn,
                  'neo4j': list_answer_neo4j}
        return answer


class Home(Resource):
    def get(self):
        return 'Q/A query stats api is up and running'


@app.route('/frontend')
def getfrontend():
    return render_template('QAsystem.html')


api.add_resource(Query, '/query')
api.add_resource(Home, '/')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
