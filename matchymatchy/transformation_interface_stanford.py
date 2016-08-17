from gensim import corpora, models, similarities
import os
import numpy

if (os.path.exists("/afs/ir/users/r/o/rohuns/Documents/deerwester.dict")):
	dictionary = corpora.Dictionary.load('/afs/ir/users/r/o/rohuns/Documents/deerwester.dict')
	corpus = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus.mm')

	dictionary_users = corpora.Dictionary.load("/afs/ir/users/r/o/rohuns/Documents/user.dict")
	corpus_users = corpora.MmCorpus('/afs/ir/users/r/o/rohuns/Documents/corpus_users.mm')
else:
	print("Could not load the dictionary")


model = models.LdaModel(corpus, id2word=dictionary, num_topics = 170, passes = 100)

# hdp = models.HdpModel(corpus, dictionary)
# lda_conversion = hdp.hdp_to_lda()
# alpha = lda_conversion[0]
# beta = lda_conversion[1]

# lda = models.LdaModel(id2word=hdp.id2word, num_topics=len(alpha), alpha=alpha, eta=hdp.m_eta)        
# lda.expElogbeta = numpy.array(beta, dtype=numpy.float32) 


model.save("/afs/ir/users/r/o/rohuns/Documents/topic_model.model")
print model.print_topics(150, 8)
#print hdp.print_topics(1500, 5)


#print lda.print_topics(200,100)

# counter = 0
# for x in hdp:
# 	counter+=1





print """



"""


# doc_probs = model[corpus]
# y = 0
# for x in doc_probs:
# 	print x
# 	y += 1
# print y
