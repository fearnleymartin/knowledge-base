"""
Micro-service restful api for Q/A queries
"""

from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


class Query(Resource):
	"""
	"""
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('query', type=list, required=True,
								   location='json')

	def post(self):
		args = self.reqparse.parse_args()
		query = args['query']
		# TODO insert query code here
		# answer = {'solr': solr_query(query),
		# 		   'rnn': rnn_query(query),
		# 		  'neo4j': neo4j_query(query)}
		answer = {'solr': ['test answer solr 1', 'test answer solr 2'],
				  'rnn': ['test answer rnn 1', 'test answer rnn 2'],
				  'neo4j': ['test answer neo4j 1', 'test answer neo4j 2']}
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