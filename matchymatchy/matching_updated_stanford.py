import gensim
from gensim import corpora, models, similarities
import os
import pickle
import csv
from collections import defaultdict

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
user_list = [] # list of user ids
new_question_list  = [] # list of question ids

raw_matching_data = csv.DictReader(open('gold_standard.csv', 'rU'))
match_list = []
for row in raw_matching_data:
	match_list.append(row)
for match in match_list:
	if(match['User ID'] in user_id_order):
		if(match['User ID'] not in user_list):
			user_list.append(match['User ID'])
		if(match['Question ID'] not in new_question_list):
			new_question_list.append(match['Question ID'])

# #add new question ids mapped with corresponding bow
new_question_dictionary = {}
for question in new_question_list:
	#print question
	index_in_corpus = question_id_order[question]
	new_question_dictionary[question] = corpus[index_in_corpus]


matched = set()

matches = [] #list of tuples (user id, question id)

for user_id in user_list:
	user_id_index = user_id_order.index(user_id)


	# # make sure I am accessing the right user
	# lists = corpus_users[user_id_index]
	# for x in lists:
	# 	word_id = x[0]
	# 	print dictionary_users[word_id]

	#topics for user	
	topics_user = model.get_document_topics(corpus_users[user_id_index], minimum_probability=0, minimum_phi_value=None, per_word_topics=False) 

	#for tup in topics_user:
	#	print tup


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



	#developing average probability topic distribution for all new questions 
	#new_question_dictionary = {"34896": corpus[0]} # question ids mapped to the bow of new questions

	new_question_topics = {}
	for question in new_question_list:
		question_probs = model.get_document_topics(new_question_dictionary[question], minimum_probability=0, minimum_phi_value=None, per_word_topics=False) 
		
		topic_probability = {}
		for tup in question_probs:
			topic_probability[tup[0]] = tup[1]


		new_question_topics[question] = topic_probability


	#defining a sumproduct when passed in two lists
	def sumproduct(list_a, list_b):
		#print len(list_a) == len(list_b)
		sum = 0.00
		for x in range(0, len(list_a)):
			sum += (list_a[x]*list_b[x])
		
		return (sum)

	# come up with probability the current user will answer each new question
	#new_question_for_user = {}

	for question in new_question_topics:
		probability_dict = new_question_topics[question]
		if(has_answered):
			non_QnA_combo = sumproduct(probability_dict.values(), topic_list_user.values()) #sumproduct of new question and non QnA avg
			QnA_combo = sumproduct(probability_dict.values(), topic_avg_previous_questions.values())
			likelihood = ((non_QnA_combo + QnA_combo)/2)*100
			#print likelihood
			if (likelihood>=1.50):
				tup = (user_id, question)
				matches.append(tup)
				matched.add(question)
		else:
			non_QnA_combo = sumproduct(probability_dict.values(), topic_list_user.values())
			likelihood = (non_QnA_combo)*100
			#print likelihood
			if (likelihood>=1.50):
				tup = (user_id, question)
				matches.append(tup)
				matched.add(question)

print matches
pickle.dump(matches, open("match_list_predicted.p", "wb"))
	

percent = (float(len(matched))/float(len(new_question_list)))*100
print "Number of questions matched = %s" %len(matched)
print "%s percent of questions were matched" %percent






