import nltk
from collections import defaultdict
from nltk.stem.wordnet import WordNetLemmatizer
import re
from gensim import corpora
from autocorrect import spell
import sys  



def create_corpus_and_dictionary(documents):
	reload(sys)  
	sys.setdefaultencoding('utf8')

	stoplist = set("""
	a
	about
	above
	after
	again
	against
	all
	am
	an
	and
	any
	are
	aren't
	as
	at
	be
	because
	been
	before
	being
	below
	between
	both
	but
	by
	can't
	cannot
	could
	couldn't
	did
	didn't
	do
	does
	doesn't
	doing
	don't
	down
	during
	each
	few
	for
	from
	further
	had
	hadn't
	has
	hasn't
	have
	haven't
	having
	he
	he'd
	he'll
	he's
	her
	here
	here's
	hers
	herself
	him
	himself
	his
	how
	how's
	i
	i'd
	i'll
	i'm
	i've
	if
	in
	into
	is
	isn't
	it
	it's
	its
	itself
	let's
	me
	more
	most
	mustn't
	my
	myself
	no
	nor
	not
	of
	off
	on
	once
	only
	or
	other
	ought
	our
	ours
	u
	a
	about
	above
	across
	after
	afterwards
	again
	against
	all
	almost
	alone
	along
	already
	also
	although
	always
	am
	among
	amongst
	amoungst
	amount
	an
	and
	another
	any
	anyhow
	anyone
	anything
	anyway
	anywhere
	are
	around
	as
	at
	back
	be
	became
	because
	become
	becomes
	becoming
	been
	before
	beforehand
	behind
	being
	below
	beside
	besides
	between
	beyond
	bill
	both
	bottom
	but
	by
	call
	can
	cannot
	cant
	co
	con
	could
	couldnt
	cry
	de
	describe
	detail
	do
	done
	down
	due
	during
	each
	eg
	eight
	either
	eleven
	else
	elsewhere
	empty
	enough
	etc
	even
	ever
	every
	everyone
	everything
	everywhere
	except
	few
	fifteen
	fify
	fill
	find
	fire
	first
	five
	for
	former
	formerly
	forty
	found
	four
	from
	front
	full
	further
	get
	give
	go
	had
	has
	hasnt
	have
	he
	hence
	her
	here
	hereafter
	hereby
	herein
	hereupon
	hers
	herse"
	him
	himse"
	his
	how
	however
	hundred
	i
	ie
	if
	in
	inc
	indeed
	interest
	into
	is
	it
	its
	itse"
	keep
	last
	latter
	latterly
	least
	less
	ltd
	made
	many
	may
	me
	meanwhile
	might
	mill
	mine
	more
	moreover
	most
	mostly
	move
	much
	must
	my
	myse"
	name
	namely
	neither
	never
	nevertheless
	next
	nine
	no
	nobody
	none
	noone
	nor
	not
	nothing
	now
	nowhere
	of
	off
	often
	on
	once
	one
	only
	onto
	or
	other
	others
	otherwise
	our
	ours
	ourselves
	out
	over
	own
	part
	per
	perhaps
	please
	put
	rather
	re
	same
	see
	seem
	seemed
	seeming
	seems
	serious
	several
	she
	should
	show
	side
	since
	sincere
	six
	sixty
	so
	some
	somehow
	someone
	something
	sometime
	sometimes
	somewhere
	still
	such
	system
	take
	ten
	than
	that
	the
	their
	them
	themselves
	then
	thence
	there
	thereafter
	thereby
	therefore
	therein
	thereupon
	these
	they
	thick
	thin
	third
	this
	those
	though
	three
	through
	throughout
	thru
	thus
	to
	together
	too
	top
	toward
	towards
	twelve
	twenty
	two
	un
	under
	until
	up
	upon
	us
	very
	via
	was
	we
	well
	were
	what
	whatever
	when
	whence
	whenever
	where
	whereafter
	whereas
	whereby
	wherein
	whereupon
	wherever
	whether
	which
	while
	whither
	who
	whoever
	whole
	whom
	whose
	why
	will
	with
	within
	without
	would
	yet
	you
	your
	yours
	yourself
	yourselves
	want
	know
	like
	interested
	good
	know
	really
	im
	i'm
	free
	problem
	solving
	hey
	hi
	hello
	name
	problem
	college
	question
	answer
	need
	work
	degree
	help
	helps
	high
	school
	lots
	excited
	passion
	best
	field
	love
	curious
	highschool
	know
	known
	extremely
	hardest
	confusing
	actually
	wants
	want
	truly
	feel
	way
	vast
	suitable
	despite
	wonder
	places
	stupid
	paths
	goals
	goal
	believe
	harder
	live
	dream
	kind
	afghanistan
	albania
	algeria
	american samoa
	andorra
	angola
	anguilla
	antarctica
	antigua and barbuda
	argentina
	armenia
	aruba
	australia
	austria
	azerbaijan
	bahamas
	bahrain
	bangladesh
	barbados
	belarus
	belgium
	belize
	benin
	bermuda
	bhutan
	bolivia
	bosnia and herzegovina
	botswana
	bouvet island
	brazil
	british indian ocean territory
	brunei darussalam
	bulgaria
	burkina faso
	burundi
	cambodia
	cameroon
	canada
	cape verde
	cayman islands
	central african republic
	chad
	chile
	china
	christmas island
	cocos (keeling islands)
	colombia
	comoros
	congo
	cook islands
	costa rica
	cote d'ivoire (ivory coast)
	croatia (hrvatska
	cuba
	cyprus
	czech republic
	denmark
	djibouti
	dominica
	dominican republic
	east timor
	ecuador
	egypt
	el salvador
	equatorial guinea
	eritrea
	estonia
	ethiopia
	falkland islands (malvinas)
	faroe islands
	fiji
	finland
	france
	france, metropolitan
	french guiana
	french polynesia
	french southern territories
	gabon
	gambia
	georgia
	germany
	ghana
	gibraltar
	greece
	greenland
	grenada
	guadeloupe
	guam
	guatemala
	guinea
	guinea-bissau
	guyana
	haiti
	heard and mcdonald islands
	honduras
	hong kong
	hungary
	iceland
	india
	indonesia
	iran
	iraq
	ireland
	israel
	italy
	jamaica
	japan
	jordan
	kazakhstan
	kenya
	kiribati
	korea
	korea
	kuwait
	kyrgyzstan
	laos
	latvia
	lebanon
	lesotho
	liberia
	libya
	liechtenstein
	lithuania
	luxembourg
	macau
	macedonia
	madagascar
	malawi
	malaysia
	maldives
	mali
	malta
	marshall islands
	martinique
	mauritania
	mauritius
	mayotte
	mexico
	micronesia
	moldova
	monaco
	mongolia
	montserrat
	morocco
	mozambique
	myanmar
	namibia
	nauru
	nepal
	netherlands
	netherlands antilles
	new caledonia
	new zealand
	nicaragua
	niger
	nigeria
	niue
	norfolk island
	northern mariana islands
	norway
	oman
	pakistan
	palau
	panama
	papua new guinea
	paraguay
	peru
	philippines
	pitcairn
	poland
	portugal
	puerto rico
	qatar
	reunion
	romania
	russian federation
	rwanda
	saint kitts and nevis
	saint lucia
	saint vincent and the grenadines
	samoa
	san marino
	sao tome and principe
	saudi arabia
	senegal
	seychelles
	sierra leone
	singapore
	slovak republic
	slovenia
	solomon islands
	somalia
	south africa
	s. georgia and s. sandwich isls.
	spain
	sri lanka
	st. helena
	st. pierre and miquelon
	sudan
	suriname
	svalbard and jan mayen islands
	swaziland
	sweden
	switzerland
	syria
	taiwan
	tajikistan
	tanzania
	thailand
	togo
	tokelau
	tonga
	trinidad and tobago
	tunisia
	turkey
	turkmenistan
	turks and caicos islands
	tuvalu
	uganda
	ukraine
	united arab emirates
	united kingdom
	united states
	us minor outlying islands
	uruguay
	uzbekistan
	vanuatu
	vatican city state
	venezuela
	vietnam
	virgin islands
	virgin islands
	wallis and futuna islands
	western sahara
	yemen
	yugoslavia
	zaire
	zambia
	zimbabwe
	a
	about
	above
	across
	after
	again
	against
	all
	almost
	alone
	along
	already
	also
	although
	always
	among
	an
	and
	another
	any
	anybody
	anyone
	anything
	anywhere
	are
	area
	areas
	around
	as
	ask
	asked
	asking
	asks
	at
	away
	b
	back
	backed
	backing
	backs
	be

	became

	because

	become

	becomes

	been

	before

	began

	behind

	being

	beings

	best

	better

	between

	big

	both

	but

	by

	c

	came

	can

	cannot

	case

	cases

	certain

	certainly

	clear

	clearly

	come

	could

	d

	did

	differ

	different

	differently

	do

	does

	done

	down

	down

	downed

	downing

	downs

	during

	e

	each

	early

	either

	end

	ended

	ending

	ends

	enough

	even

	evenly

	ever

	every

	everybody

	everyone

	everything

	everywhere

	f

	face

	faces

	fact

	facts

	far

	felt

	few

	find

	finds

	first

	for

	four

	from

	full

	fully

	further

	furthered

	furthering

	furthers

	g

	gave

	general

	generally

	get

	gets

	give

	given

	gives

	go

	going

	good

	goods

	got

	great

	greater

	greatest

	group

	grouped

	grouping

	groups

	h

	had

	has

	have

	having

	he

	her

	here

	herself

	high

	high

	high

	higher

	highest

	him

	himself

	his

	how

	however

	i

	if

	important

	in

	interest

	interested

	interesting

	interests

	into

	is

	it

	its

	itself

	j

	just

	k

	keep

	keeps

	kind

	knew

	know

	known

	knows

	l

	large

	largely

	last

	later

	latest

	least

	less

	let

	lets

	like

	likely

	long

	longer

	longest

	m

	made

	make

	making

	man

	many

	may

	me

	member

	members

	men

	might

	more

	most

	mostly

	mr

	mrs

	much

	must

	my

	myself

	n

	necessary

	need

	needed

	needing

	needs

	never

	new

	new

	newer

	newest

	nextturned

	turning

	turns

	two

	u

	under

	until

	up

	upon

	us

	use

	used

	uses

	v

	very

	w

	want

	wanted

	wanting

	wants

	was

	way

	ways

	we

	well

	wells

	went

	were

	what

	when

	where

	whether

	which

	while

	who

	whole

	whose

	why

	will

	with

	within

	without

	work

	worked

	working

	works

	would

	x

	y

	year

	years

	yet

	you

	young

	younger

	youngest

	your

	yours

	no

	nobody

	non

	noone

	not

	nothing

	now

	nowhere

	number

	numbers

	o

	of

	off

	often

	old

	older

	oldest

	on

	once

	one

	only

	open

	opened

	opening

	opens

	or

	order

	ordered

	ordering

	orders

	other

	others

	our

	out

	over

	p

	part

	parted

	parting

	parts

	per

	perhaps

	place

	places

	point

	pointed

	pointing

	points

	possible

	present

	presented

	presenting

	presents

	problem

	problems

	put

	puts

	q

	quite

	r

	rather

	really

	right

	right

	room

	rooms

	s

	said

	same

	saw

	say

	says

	second

	seconds

	see

	seem

	seemed

	seeming

	seems

	sees

	several

	shall

	she

	should

	show

	showed

	showing

	shows

	side

	sides

	since

	small

	smaller

	smallest

	so

	some

	somebody

	someone

	something

	somewhere

	state

	states

	still

	still

	such

	sure

	t

	take

	taken

	than

	that

	the

	their

	them

	then

	there

	therefore

	these

	they

	thing

	things

	think

	thinks

	this

	those

	though

	thought

	thoughts

	three

	through

	thus

	to

	today

	together

	too

	took

	toward

	turn

	




	aimee
	join
	makes
	friend
	continue
	suggest
	suggests
	hi
	path
	month
	tell
	wrong
	wait
	question
	questions
	hiring
	wonder
	wondering
	university
	freshman
	sophomore
	junior
	senior
	careeer
	thank
	hello
	rn
	try
	grad
	Aimee
	aimee



	""".split()) #http://www.ranks.nl/stopwords and http://xpo6.com/list-of-english-stop-words/
	# extra stop words to play with
	# develop the corpus for the questions
	# reload(sys)  
	# sys.setdefaultencoding('utf8')
	texts = []
	spell_checked_words = {}
	document_length = float(len(documents))
	counter = 0.0

	print"processing docs"
	for document in documents:
		document = document.lower()
		document_split = re.split('[?@&!;/.,\s+]', document)
		clean_document_split = filter(lambda a: a != '', document_split)


		#lemmatize and spell check
		lemmatized_and_spelled_document_split = []
		lmtzr = WordNetLemmatizer()
		for word in clean_document_split:
			if word not in stoplist:
				word_spelled = ""
				if(word in spell_checked_words):
					word_spelled = spell_checked_words[word]
				else:
					word_spelled = spell(word)
					spell_checked_words[word] = word_spelled

				word_spelled = spell(word)
				word_lemmatized = lmtzr.lemmatize(word_spelled, 'n')
				lemmatized_and_spelled_document_split.append(word_lemmatized)


		#POS tagger
		pos_tuple_list = nltk.pos_tag(lemmatized_and_spelled_document_split)
		document_list = []
		for tup in pos_tuple_list:
			if tup[1] == "NN" or tup[1] == "NNS":
				word = tup[0]
				if word not in stoplist:
					document_list.append(word)
					#print word


		#seperates based on dashes
		length = len(document_split)
		for x in range (0, length):
			word = document_split[x]
			if(word.find('-') != -1):
				separated = re.split('-', word)
				#lemmatize and spell check the separated words and then add it to the list of words for that document
				for token in separated:
					word = lmtzr.lemmatize(word, 'n')
					document_list.append(token)
	



		texts.append(document_list)
		counter += 1
		percent = (counter/ document_length)*100
		print "\r%s of documents have been processed" %percent


	#print texts[1]
	frequency = defaultdict(int)
	for text in texts:
		for token in text:
				frequency[token] += 1

	

	texts = [[token for token in text if frequency[token] > 1] for text in texts]
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]

	tup = (corpus, dictionary)

	return tup