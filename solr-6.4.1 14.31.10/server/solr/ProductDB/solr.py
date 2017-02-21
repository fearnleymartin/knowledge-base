import urllib3
with open('test.json', 'rb') as data_file:
    my_data = data_file.read()
req = urllib3.Request(url='http://localhost:8983/solr/update/json?commit=true',
                      data=my_data)
req.add_header('Content-type', 'application/json')
f = urllib3.urlopen(req)
# Begin using data like the following
print(f.read())