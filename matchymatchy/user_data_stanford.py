import csv
import datetime
import os
from ast import literal_eval
import re
from collections import defaultdict
from pprint import pprint
from gensim import corpora
import pickle
from tokenizing import create_corpus_and_dictionary 



raw_user_data = csv.DictReader(open('cv_users_utf8_csv_10k.csv', 'rU'))
user_list = []
user_id_order = {}

counter = 0
for row in raw_user_data:
	if(row["account_type"] != "S"):
		user_list.append(row)
		user_id_order[row["id"]] = counter
		counter += 1

#print user_id_order
pickle.dump(user_id_order, open("user_id_list.p", "wb"))

user_documents = []
for user in user_list:
	user_topics_text = (((user['topics_followed'])[3:-2]).replace("u'", "")).replace("'", "")
	user_text = user['headline'] + " " +user_topics_text + " " + user['industry']
	user_documents.append(user_text)

tup = create_corpus_and_dictionary(user_documents)
corpus_users = tup[0]
dictionary_users = tup[1]

# dictionary_users.save('/afs/ir/users/r/o/rohuns/Documents/user.dict')
# corpora.MmCorpus.serialize('/afs/ir/users/r/o/rohuns/Documents/corpus_users.mm', corpus_users)

# stoplist = set("""
# a
# about
# above
# after
# again
# against
# all
# am
# an
# and
# any
# are
# aren't
# as
# at
# be
# because
# been
# before
# being
# below
# between
# both
# but
# by
# can't
# cannot
# could
# couldn't
# did
# didn't
# do
# does
# doesn't
# doing
# don't
# down
# during
# each
# few
# for
# from
# further
# had
# hadn't
# has
# hasn't
# have
# haven't
# having
# he
# he'd
# he'll
# he's
# her
# here
# here's
# hers
# herself
# him
# himself
# his
# how
# how's
# i
# i'd
# i'll
# i'm
# i've
# if
# in
# into
# is
# isn't
# it
# it's
# its
# itself
# let's
# me
# more
# most
# mustn't
# my
# myself
# no
# nor
# not
# of
# off
# on
# once
# only
# or
# other
# ought
# our
# ours
# u
# a
# about
# above
# across
# after
# afterwards
# again
# against
# all
# almost
# alone
# along
# already
# also
# although
# always
# am
# among
# amongst
# amoungst
# amount
# an
# and
# another
# any
# anyhow
# anyone
# anything
# anyway
# anywhere
# are
# around
# as
# at
# back
# be
# became
# because
# become
# becomes
# becoming
# been
# before
# beforehand
# behind
# being
# below
# beside
# besides
# between
# beyond
# bill
# both
# bottom
# but
# by
# call
# can
# cannot
# cant
# co
# con
# could
# couldnt
# cry
# de
# describe
# detail
# do
# done
# down
# due
# during
# each
# eg
# eight
# either
# eleven
# else
# elsewhere
# empty
# enough
# etc
# even
# ever
# every
# everyone
# everything
# everywhere
# except
# few
# fifteen
# fify
# fill
# find
# fire
# first
# five
# for
# former
# formerly
# forty
# found
# four
# from
# front
# full
# further
# get
# give
# go
# had
# has
# hasnt
# have
# he
# hence
# her
# here
# hereafter
# hereby
# herein
# hereupon
# hers
# herse"
# him
# himse"
# his
# how
# however
# hundred
# i
# ie
# if
# in
# inc
# indeed
# interest
# into
# is
# it
# its
# itse"
# keep
# last
# latter
# latterly
# least
# less
# ltd
# made
# many
# may
# me
# meanwhile
# might
# mill
# mine
# more
# moreover
# most
# mostly
# move
# much
# must
# my
# myse"
# name
# namely
# neither
# never
# nevertheless
# next
# nine
# no
# nobody
# none
# noone
# nor
# not
# nothing
# now
# nowhere
# of
# off
# often
# on
# once
# one
# only
# onto
# or
# other
# others
# otherwise
# our
# ours
# ourselves
# out
# over
# own
# part
# per
# perhaps
# please
# put
# rather
# re
# same
# see
# seem
# seemed
# seeming
# seems
# serious
# several
# she
# should
# show
# side
# since
# sincere
# six
# sixty
# so
# some
# somehow
# someone
# something
# sometime
# sometimes
# somewhere
# still
# such
# system
# take
# ten
# than
# that
# the
# their
# them
# themselves
# then
# thence
# there
# thereafter
# thereby
# therefore
# therein
# thereupon
# these
# they
# thick
# thin
# third
# this
# those
# though
# three
# through
# throughout
# thru
# thus
# to
# together
# too
# top
# toward
# towards
# twelve
# twenty
# two
# un
# under
# until
# up
# upon
# us
# very
# via
# was
# we
# well
# were
# what
# whatever
# when
# whence
# whenever
# where
# whereafter
# whereas
# whereby
# wherein
# whereupon
# wherever
# whether
# which
# while
# whither
# who
# whoever
# whole
# whom
# whose
# why
# will
# with
# within
# without
# would
# yet
# you
# your
# yours
# yourself
# yourselves
# want
# know
# like
# interested
# good
# knowly
# im
# i'm

# real

# """.split()) #http://www.ranks.nl/stopwords and http://xpo6.com/list-of-



# user_bow = []

# for doc in user_documents:
# 	doc = doc.lower()
# 	user_split = re.split('[-?!;/.,\s+]', doc) # add a way to retain the dash
	
# 	user_list = []
# 	for words in user_split:
# 		if words not in stoplist:
# 			if words: #takes out empty strings after a punctuation
# 				user_list.append(words)
# 	user_bow.append(user_list)


# frequency_users = defaultdict(int)
# for users in user_bow:
# 	for token in users:
# 		frequency_users[token] += 1



# user_bow = [[token for token in text if frequency_users[token] > 1] for text in user_bow]

# dictionary_users = corpora.Dictionary(user_bow)
# dictionary_users.save('/afs/ir/users/r/o/rohuns/Documents/user.dict')

# print dictionary_users[221]

# corpus_users = [dictionary_users.doc2bow(text) for text in user_bow]
# corpora.MmCorpus.serialize('/afs/ir/users/r/o/rohuns/Documents/corpus_users.mm', corpus_users)
# #pprint(corpus_users)
# print len(user_id_order)
