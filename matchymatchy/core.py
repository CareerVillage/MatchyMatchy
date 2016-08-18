# Let's match some requests to some users! At a high level, this code
# defines the "universe" of possible matches, calculates who should get
# notified for each question, and then sends the notifications.

#############################################
# Imports
#############################################

import Queue
from datetime import datetime, timedelta
from forum.models import Question, Users
from collections import defaultdict
from forum.utils.mail import send_template_email
from forum.models import User, Question, Tag, MarkedTag





#############################################
# Begin calculation and send notifications
#############################################

def email_notification(valid_users, node_email_max, notifications_template, notifications_lookup):
    question_email_count = defaultdict(int)#keeps count of how many times the email has been notified and is initialized with the key being all valid questions and the intial count to 0    
    valid_questions = get_valid_questions() #filters for deleted, closed, comments, and greater than or equal to 4 answers. Applicable for all users
    valid_users = get_valid_users(notifications_lookup)
    
    for user in valid_users:
        user_tags = user.tag_selections.all(notifications_timedelta) #why is notifications_timedelta passed in here? I may have done this on accident but want to check with you. I looked at how user was setup and could not tell
        
        # filters for country tags
        if user.notify_countries_only:
                country_tags = [marked_tag.tag.id for marked_tag in
                                MarkedTag.objects.filter(
                                    user=user,
                                    tag__tag_types__name__iexact='country')]
                # If the user follows 'Global' then send all the questions
                try:
                    tag_global = Tag.objects.get(code='00').id
                except Tag.DoesNotExist:
                    print 'Tag "Global" does not exist'
                if country_tags and not (tag_global in country_tags):
                    valid_questions_country = questions.filter(tags__id__in=country_tags)
                elif not country_tags:
                    valid_questions_country = None



        #Filter for user specific filters (tags, answered before)
        questions_for_current_user = valid_questions_country.exclude(
            children__author=user
            ).filter(
                tags__id__in=user.tag_selections.filter(
                    Q(reason='good') & Q(tag__tag_types__name__iexact='topic')
                ).values_list('tag_id', flat=True).query
            ).distinct()

        #excludes if user previously notified for this question (TO DO)
        user_nodes_notified_in_the_past = EmailSent.objects.filter(recipient=user).values_list('nodes').distinct() # TO DO: REVIEW THIS CODE


        user_question_queue = Queue.PriorityQueue()  #initialize queue of questions for the user
        for question in questions_for_current_user:
            if not question in user_nodes_notified_in_the_past: #check if the user has been notified about the question
                if not question_email_count[question] or not question_email_count[question] > 40: #check if the question has not already been emailed too many times
                    score = calculate_score(user, question) * (-1) # negative to be able to use a priority queue properly (lower numbers are higher priority)
                    user_question_queue.put(question, score) #add question to the queue
        
        #develop the email question list for current user
        email_questions = []
        for limit in range(0, (node_email_max)-1): 
            if not(user_question_queue.empty):
                question_object = user_question_queue.get() #pull question out from priority queue
                email_questions.append(question_object)
                question_email_count[question_object] += 1  #increase the email count for that question in the tracking dict
            else:
                break 

        #email questions
        if email_questions:
                print 'Sending notification to %s with %d questions.' % (user, email_questions.count())

                send_template_email([user], notifications_template, {
                    'questions': questions,
                }, nodes=questions)







#############################################
# How match scores are calculated
#############################################

def calculate_score(user, question):
    timeliness = calculate_timeliness(question) #prioritization of when the question was asked
    need = calculate_if_new_answers_needed(question) #prioritize based on how many answers the question already has, does it need more questions
    popularity = calculate_popularity(question) # this may be a v2 implementation
    users_interacted_before = interacted_before(user, question) #to determine if the users have had an interaction with each other before

    score = (1.5*timeliness + 1.5*need + popularity + 2*users_interacted_before)
    return score

def calculate_timeliness(question):
    today = datetime.date.today()
    time_delta = today - question.dateAsked() #TO DO check if this is right?

    #TO DO is the format for time_delta correct
    if (time_delta < 7): # 1 week
        one_week = 5 #used a random number
        return one_week
    elif (time_delta < 30): # 1 month
        one_month = 4
        return one_month
    elif (time_delta < 90):
        three_month = 3
        return three_month
    elif (time_delta < 180):
        six_month = 2
        return six_month
    else:
        nine_month = 1
        return nine_month

def calculate_need(question):
    number_of_answers = question.numberOfAnswers()

    if (number_of_answers < 1): 
        score_boost = 5 #used a random number
        return score_boost
    elif (number_of_answers < 2): 
        score_boost = 3
        return score_boost
    elif (number_of_answers < 3):
        score_boost = 2
        return score_boost
    else (number_of_answers < 4):
        score_boost = 1
        return score_boost


def calculate_popularity(question):
    question_views = question.numberOfViews() 
    score = 0
    if(question_views > ): #TO DO determine what number of views we consider high and low
        score = 5
        return score
    elif(question_views > ):
        score = 4
        return score
    elif(question_views > ):
        score = 3
        return score
    elif(question_views > ):
        score = 2
        return score
    elif(question_views > ):
        score = 1
        return score
    else:
        return score

    #similar to the last two create some sort of a sliding scale for incrementing the score as views go up with a max cap of influence

    return max_score

def interacted_before(user, current_question):
    questions_answered = user.questionsAnswered() #TO DO is this the right syntax, I went into the user model and think this is right
    interacted = false
    for question in questions_answered:
        if (question.student == current_question.student):
            interacted = true
            break
    if interacted:
        interacted_score = 5
        return interacted_score
    else:
        not_interacted_score = 0
        return not_interacted_score









#############################################
# Define matchable universe of items
#############################################








def get_valid_questions():
    today = datetime.date.today()
    earliest_valid_date = today - datetime.timedelta(weeks=(52/12*9))
    q = (Question.objects
        .filter_state(deleted=False, closed=False)
        .filter(added_at__gt=earliest_valid_date)
        # Django gets strange when you filter before annotating
        .filter(children__node_type='answer') # Exclude comments  #TO DO why is this needed?
        .annotate(c=Count('children')) # Count answer children
        .filter(c__lt=4) # filter out questions with 4+ answers
        )
    return q



def get_valid_users(notifications_lookup):
    q = Q(notifications=notifications_lookup)
        if settings.djsettings.DEFAULT_NOTIFICATIONS == notifications_lookup:
            q |= Q(notifications=None)

    u = User.objects.filter(q)
    return u








