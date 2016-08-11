import gensim
from gensim import corpora, models, similarities
import os
import pickle

if (os.path.exists("/afs/ir/users/r/o/rohuns/Documents/deerwester.dict")):
	dictionary = corpora.Dictionary.load('/afs/ir/users/r/o/rohuns/Documents/deerwester.dict')
	corpus = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus.mm')

	dictionary_users = corpora.Dictionary.load("/afs/ir/users/r/o/rohuns/Documents/user.dict")
	corpus_users = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus_users.mm')
else:
	print("Could not load the dictionary")


model = gensim.models.LdaModel.load("/afs/ir/users/r/o/rohuns/Documents/topic_model.model")

doc_probs = model[corpus]


question_count = 0
min_threshold = 0.25
half_threshold = 0.5
num_above_min = 0.0
num_above_half = 0.0
for doc in doc_probs:
	question_best_topic = (0,0)
	for tup in doc:
		if tup[1] > question_best_topic[1]:
			question_best_topic = tup

	if question_best_topic[1] >= min_threshold:
		num_above_min += 1
	if question_best_topic[1] >= half_threshold:
		num_above_half += 1
	question_count += 1


number_unmatched = question_count - num_above_min
matched_percent = (num_above_min/question_count)*100
half_matched_percent = (num_above_half/question_count)*100
print "The percent of questions that are above the threshold: " + str(min_threshold) + " is " + str(matched_percent) + "%"
print "This means " + str(number_unmatched) + " questions were left unmatched"
print "The percent above 0.5: " + str(half_matched_percent)


# coherence info

counter = 0
total = 0.000
for doc in model.top_topics(corpus, num_words=20):
	total += doc[1]
	counter += 1


avg = total/counter
print "You average coherence over the topics is: " + str(avg)
