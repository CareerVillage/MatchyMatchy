import gensim
from gensim import corpora, models, similarities
import os
import pickle
import csv
from collections import defaultdict
import random
import ast

if (os.path.exists("/afs/ir/users/r/o/rohuns/Documents/deerwester.dict")):
	dictionary = corpora.Dictionary.load('/afs/ir/users/r/o/rohuns/Documents/deerwester.dict')
	corpus = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus.mm')

	dictionary_users = corpora.Dictionary.load("/afs/ir/users/r/o/rohuns/Documents/user.dict")
	corpus_users = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus_users.mm')
else:
	print("Could not load the dictionary")



#load models and relevant files
model = gensim.models.LdaModel.load("/afs/ir/users/r/o/rohuns/Documents/topic_model.model")


question_id_order = dict(pickle.load( open("question_id_list.p", "rb")))
user_id_order = list(pickle.load( open("user_id_list.p", "rb")))


#load gold standard data
#new_question_list = ['7918']

new_question_list= """
33245
3168
30181
27867
25338
4326
25885
7918
6740
6457
3015
12856
24108
29400
23853
3431
20251
29743
18385
8844
30440
7682
30175
19513
21872
27929
23669
3413
671
23947
35578
37504
103
12062
34254
35959
3177
17486
23322
28712
1556
4014
26021
26032
36817
32438
30208
29922
30530
7402""".split() 


random_user_list = """
19575
7994
11527
8952
13892
7674
14697
9386
2379
14076
14198
479
3426
2867
12137
6363
14371
10505
7619
7655
22247
3920
2203
7709
11536
14251
5167
6627
14452
5941
16494
8209
13900
8890
15059
13726
22308
14482
11280
12212
992
9354
12626
15586
11509
21768
21327
8822
1819
10176
""".split()
#random_user_list = random.sample(user_id_order, x) # list of user ids




#y = 50 #number of random users
#new_question_list  = random.sample(question_id_order, y) # list of question ids




#read and save question profiles in dict to their id number
question_info = {}
question_tags_dict= {}

raw_question_data = csv.DictReader(open('cv_questions_utf8_csv_10k.csv', 'rU'))
question_list = []
for row in raw_question_data:
	if(row['id'] in new_question_list):
		question_list.append(row)

for question in question_list:
	question_body_modified =  (question["body"])[3:-4] #takes out the paragraph html headers
	question_tags = question['tagname_list']
	question_text = question['title'] + " "+ question_body_modified + " Tags: "+ question_tags
	
	question_text = question_text.replace("<p>", "")
	question_text = question_text.replace("</p>", "")
	question_text = question_text.replace("<li>", "")
	question_text = question_text.replace("</li>", "")
	question_text = question_text.replace("<br>", "")
	question_text = question_text.replace("<br>", "")
	
	question_info[question['id']] = question_text

	#add individual tags to a dict
	list_of_tags_questions = (question_tags.lower()).split()
	set_of_tags_users = set()
	for tag in list_of_tags_questions:
		set_of_tags_users.add(tag)


	question_tags_dict[question['id']] = set_of_tags_users



# read and save user profiles in dict to their id number
user_info = {}
user_tags_dict = {}

raw_user_data = csv.DictReader(open('cv_users_utf8_csv_10k.csv', 'rU'))
user_list = []
for row in raw_user_data:
	if(row["id"] in random_user_list):
		user_list.append(row)

for user in user_list:
	user_topics_text = (((user['topics_followed'])[3:-2]).replace("u'", "")).replace("'", "")
	user_text = "Headline: " + user['headline'] + " Topics Followed: " +user_topics_text + " Industry: " + user['industry']
	user_info[user['id']] = user_text
	
	#get tags of user
	list_of_tags_users_string = user['topics_followed']
	list_of_tags_users_string = ast.literal_eval(list_of_tags_users_string)
	list_of_tags_users = list(list_of_tags_users_string)
	set_of_tags_questions = set()

	for tag in list_of_tags_users:
		tag_lower = tag.lower()
		set_of_tags_questions.add(tag_lower)
	user_tags_dict[user['id']] = set_of_tags_questions



#rows of information that will go into the csv. Formatted as ['question_id','question_text','author_id','author_text', 'topic_model_match', 'string_match']
list_of_rows = []

#actual matching process


#add new question ids mapped with corresponding bow
new_question_dictionary = {}
for question in new_question_list:
	index_in_corpus = question_id_order[question]
	new_question_dictionary[question] = corpus[index_in_corpus]


matched = set()

matches = [] #list of tuples (user id, question id)

for user_id in random_user_list:
	user_id_index = user_id_order.index(user_id)



	#topics for user	
	topics_user = model.get_document_topics(corpus_users[user_id_index], minimum_probability=0, minimum_phi_value=None, per_word_topics=False) 
	# print "non QA data"
	#print model[corpus_users[user_id_index]]

	# for tup in corpus_users[user_id_index]
	# 	print dictionary_users[tup[0]]

	# print topics_user


	#dictionary for non-QA matching topics to  of all topics that user falls into
	topic_list_user = {}
	for tup in topics_user:
		topic_list_user[tup[0]] = tup[1]

	#collect  QnA data
	raw_answer_data = csv.DictReader(open('cv_answers_utf8_csv_10k.csv', 'rU'))
	answered_question_ids = []
	for row in raw_answer_data:
		if row["author.id"] == user_id:
			answered_question_ids.append(row["id_of_question_being_answered"])

	has_answered = (len(answered_question_ids) != 0)
	if(has_answered):
		question_list_probabilities = {}
		for question_id in answered_question_ids:
			index = question_id_order[question_id]
			question_list_probabilities[index] = model.get_document_topics(corpus[index], minimum_probability = 0, minimum_phi_value = None, per_word_topics = False)

			

	# create QnA vector average
	if(has_answered):
		topics_sum = defaultdict(int)
		for question in question_list_probabilities:
			for tup in question_list_probabilities[question]:
				topics_sum[tup[0]] += tup[1]

		topic_avg_previous_questions = {}
		for topic in topics_sum:
			topic_avg_previous_questions[topic] = (topics_sum[topic])/len(question_list_probabilities)
		
		#print topic_avg_previous_questions


	#developing average probability topic distribution for all new questions 
	#new_question_dictionary = {"34896": corpus[0]} # question ids mapped to the bow of new questions

	new_question_topics = {}
	for question in new_question_list:
		question_probs = model.get_document_topics(new_question_dictionary[question], minimum_probability=0, minimum_phi_value=None, per_word_topics=False) 
		# print question_probs

		# print "alternate"
		#print model[new_question_dictionary[question]]
		# for tup in new_question_dictionary[question]:
		# 	print dictionary[tup[0]]



		topic_probability = {}
		for tup in question_probs:
			topic_probability[tup[0]] = tup[1]


		new_question_topics[question] = topic_probability


	#defining a sumproduct when passed in two lists
	def sumproduct(dict_a, dict_b):
		#print len(list_a) == len(list_b)
		# sum = 0.00
		# for x in range(0, len(list_a)):
		# 	sum += (list_a[x]*list_b[x])
		
		# return (sum)

		#if pass in dictionary 
		total = 0.00
		for topic in dict_a:
			total+= (dict_a[topic]*dict_b[topic])
		return total



	# come up with probability the current user will answer each new question
	#new_question_for_user = {}

	for question in new_question_topics:
		probability_dict = new_question_topics[question]

		#string match
		string_match = 'No'
		user_tags_set = user_tags_dict[user_id]
		question_tags_set = question_tags_dict[question]
		if(len(user_tags_set.intersection(question_tags_set)) > 0):
			string_match = 'Yes'




		if(has_answered):
			#print probability_dict.keys()[0:169]
			#print topic_list_user.keys()[0:169]
			non_QnA_combo = sumproduct(probability_dict, topic_list_user) #sumproduct of new question and non QnA avg
			QnA_combo = sumproduct(probability_dict, topic_avg_previous_questions)

			likelihood = ((non_QnA_combo + QnA_combo)/2)*100
			# if(non_QnA_combo>QnA_combo):
			# 	larger_val = non_QnA_combo
			# else:
			# 	larger_val = QnA_combo

			# likelihood = larger_val
			#print likelihood
			if (likelihood>=2):
				tup = (user_id, question)
				matches.append(tup)
				matched.add(question)
				list_of_rows.append([question,question_info[question],user_id,user_info[user_id], 'Yes', string_match])
			else:
				list_of_rows.append([question,question_info[question],user_id,user_info[user_id], 'No', string_match])

		else:
			non_QnA_combo = sumproduct(probability_dict, topic_list_user)
			likelihood = (non_QnA_combo)*100
			#print likelihood
			if (likelihood>=2):
				tup = (user_id, question)
				matches.append(tup)
				matched.add(question)
				list_of_rows.append([question,question_info[question],user_id,user_info[user_id], 'Yes', string_match])
			else:
				list_of_rows.append([question,question_info[question],user_id,user_info[user_id], 'No', string_match])

pickle.dump(matches, open("match_list_predicted.p", "wb"))
# actual matching completion resulting in a list of tuples in a list called "matches"

#filling out the csv
with open('/afs/ir/users/r/o/rohuns/Documents/spreadsheet.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['question_id','question_text','author_id','author_text', 'topic_model_match', 'string_match'])

    for row in list_of_rows:
    	writer.writerow(row)
percent = (float(len(matched))/float(len(new_question_list)))*100
print "Number of questions matched = %s" %len(matched)
print "%s percent of questions were matched" %percent


# lis_topic_words = model.get_topic_terms(89, topn =20)
# for tup in lis_topic_words:
# 	print dictionary[tup[0]]



