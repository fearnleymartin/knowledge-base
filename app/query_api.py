"""
Micro-service restful api for Q/A queries
"""

from flask import Flask
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)


class SolrQuery(Resource):
	"""
	"""
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('query', type=list, required=True,
								   location='json')

	def post(self):
		args = self.reqparse.parse_args()
		query = args['query']
		# TODO insert SOLR query code here
		#answer = solr_query(query)
		answer = {'answer': 'test answer'}
		return answer

class RnnQuery(Resource):
	"""
	"""
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('query', type=list, required=True,
								   location='json')

	def post(self):
		args = self.reqparse.parse_args()
		query = args['query']
		# TODO insert RNN query code here
		#answer = rnn_query(query)
		answer = {'answer': 'test answer'}
		return answer


class Neo4jQuery(Resource):
	"""
	"""
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('query', type=list, required=True,
								   location='json')



	def post(self):
		args = self.reqparse.parse_args()
		query = args['query']
		# TODO insert NEO4j query code here
		#answer = neo4j_query(query)
		answer = {'answer': 'test answer'}
		return answer


class Home(Resource):
	def get(self):
		return 'Q/A query stats api is up and running'


api.add_resource(SolrQuery, '/solr')
api.add_resource(RnnQuery, '/rnn')
api.add_resource(Neo4jQuery, '/neo4j')
api.add_resource(Home, '/')

if __name__ == '__main__':
	app.run(port=5000, debug=True)