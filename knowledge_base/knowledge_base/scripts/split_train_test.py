"""
The super user crawler data set contains a large set of Q/A. Some of these question are duplicates of other questions. We want to use duplicate questions and their originals and evaluation for the retrieval models.
This code is intended to separate the set into two set:
- a test set containing all the duplicate questions and their original urls
- a train set containing all the rest
"""
import json

input_file_path = ''
train_file_path = ''
test_file_path = ''

domain = ''

duplicate_urls = set()
original_urls = set()
with open(input_file_path) as f:
	for line in f.readlines():
		j_content = json.loads(line)
		if 'question_original_url' in j_content['question'].keys():
			duplicate_urls.add(j_content['source_url'])
			original_urls.add(domain + j_content['question']['question_original_url'])

train_count = 0
test_count = 0
lonely_duplicates = 0

with open(input_file_path) as f:
	lines = f.readlines()
	with open(train_file_path, 'w') as f_train:
		with open(test_file_path, 'w') as f_test:
			for line in f:
				j_content = json.loads(line)
				if j_content['source_url'] in duplicate_urls:
					f_test.write(json.dumps(j_content) + '\n')
					test_count += 1
					if j_content['question_original_url'] not in original_urls:
						lonely_duplicates += 1
				elif j_content['source_url'] in original_urls:
					f_test.write(json.dumps(j_content) + '\n')
					test_count += 1
				else:
					f_train.write(json.dumps(j_content) + '\n')
					train_count += 1


