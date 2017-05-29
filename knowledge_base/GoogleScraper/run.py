from knowledge_base.GoogleScraper.GoogleScraper import GoogleScraper

"""
Specify a query, a Google domain and a language code in the dictionary d
Will return list of the top 100 search results for given parameters
"""

s = GoogleScraper()
d = {
		'parsed_keyword' : 'iPhone troubleshooting',
		'domain':'google.com',
		'lang_code':'en'
	}
s.get_google_result_urls_for_keyword(**d) # return a boolean
print(s.google_result_urls)