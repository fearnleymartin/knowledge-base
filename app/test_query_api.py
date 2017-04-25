import requests

url = 'http://127.0.0.1:5000'

t = requests.get(url)
print(t.text)

def test_convex_opt():
	query = 'test query'
	payload = {'query': query}
	r = requests.post(url+'/solr', json=payload)
	print(r.json())