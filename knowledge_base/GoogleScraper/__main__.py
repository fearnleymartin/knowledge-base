from identification.googlescraper import GoogleScraper

s=GoogleScraper()
d = {'parsed_keyword' : 'test', 'domain':'google.fr','lang_code':'fr'}
s.get_google_result_urls_for_keyword(**d) #return a boolean
print(s.google_result_urls)