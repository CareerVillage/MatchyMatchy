import pickle
import csv

raw_match_data = csv.DictReader(open('gold_standard.csv', 'rU'))
match_list = []
for row in raw_match_data:
	match_list.append(row)


matches_predicted = pickle.load( open("match_list_predicted.p", "rb")) #the format of this data will be a dictionary (key = user_id, value = list of question_id)
correct = 0
incorrect = 0


predicted_yes_correctly = 0
predicted_no_correctly = 0
predicted_yes_incorrectly = 0
predicted_no_incorrectly = 0
for match in match_list:
	if((match["User ID"], match["Question ID"]) in matches_predicted):
		if (match["Relevance"] == "Yes"):
			correct +=1
			predicted_yes_correctly += 1
		else:
			incorrect += 1
			predicted_yes_incorrectly += 1
	else:
		if(match["Relevance"] == "No"):
			correct += 1
			predicted_no_correctly += 1
		else:
			incorrect += 1
			predicted_no_incorrectly += 1

total = incorrect+correct
print "The total number of responses should be 160. It is: " + str(total)

precision = (float(correct)/float(total))*100

print "The precision of this matching round was: " + str(precision)

print "The incorrect amount = " + str(incorrect) + " and the correct number was = " + str(correct)

print "Predicted yes correctly: " + str(predicted_yes_correctly)
print "Predicted no correctly: " + str(predicted_no_correctly)
print "Predicted yes incorrectly: " + str(predicted_yes_incorrectly)
print "Predicted no incorrectly: " + str(predicted_no_incorrectly)








# correct_predictions = 0


# for user in matches:




# total_matched = len(correct_list)
# total_predicted = len(predicted_list)
# correctly_predicted = len(set(correct_list).intersection(predicted_list))

# # Calculate (and print) the f-measure
# precision = float(correctly_predicted) / float(total_predicted) # Calculate precision
# recall = float(correctly_predicted) / float(total_matched) # Calculate recall
# if correctly_predicted > 0:
#     f1 = 2 * ( precision * recall) / float(precision + recall)
# else:
#     f1 = 0.0

# print "precision: %s" % precision 
# print "recall: %s" % recall
# print "f1: %s" % f1
