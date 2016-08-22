# Let's match some requests to some users! At a high level, this code
# defines the "universe" of possible matches, calculates who should get
# notified for each question, and then sends the notifications.

#############################################
# Imports
#############################################

import Queue
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from collections import defaultdict
from forum.utils.mail import send_template_email
from forum.models import User, Question, Tag, MarkedTag
from forum import settings
from django.db.models import Q
from django.db.models import Count





#############################################
# Begin calculation and send notifications
#############################################

def email_notification(node_email_max, notifications_template, notifications_lookup):
    question_email_count = defaultdict(int)#keeps count of how many times the email has been notified and is initialized with the key being all valid questions and the intial count to 0    
    
    for user in get_valid_users(notifications_lookup):
        # null, false, or true
        #users can follow countries global ,specific, or none
        #if they never follow countries (treat as global)
        #else 
            #(if notif... == false or the follow global) treat them sas global
            #else () only send notifications for countries they follow
        # filters for country tags
        if (user.notify_countries_only==False): #set to false(meaning they want global)
            questions_for_current_user = get_valid_questions()
        else: #null or true
           country_tags = [marked_tag.tag.id for marked_tag in
                        MarkedTag.objects.filter(
                            user=user,
                            tag__tag_types__name__iexact='country')]
            # If the user follows 'Global' then send all the questions
            try:
                tag_global = Tag.objects.get(code='00').id
            except Tag.DoesNotExist:
                print 'Tag "Global" does not exist'
            if country_tags and not (tag_global in country_tags): #global not in country tags
                questions_for_current_user = get_valid_questions().filter(tags__id__in=country_tags) 
            # elif not country_tags: #do not follow any countries
            #     questions_for_current_user = None
            else: #has no country tags or follow global
                questions_for_current_user = get_valid_questions()


        #Filter for user specific filters (tags, answered before)
        questions_for_current_user = questions_for_current_user.exclude(
            children__author=user
            ).filter(
                tags__id__in=user.tag_selections.filter(
                    Q(reason='good') & Q(tag__tag_types__name__iexact='topic')
                ).values_list('tag_id', flat=True).query
            ).distinct()

            
        user_node_ids_notified_in_the_past = EmailSent.objects.filter(recipient=user, nodes__node_type='question', nodes__isnull=False).values_list('nodes', flat=True).distinct()

        user_question_queue = Queue.PriorityQueue()  #initialize queue of questions for the user
        for question in questions_for_current_user:
            if not question.id in user_nodes_notified_in_the_past: #check if the user has been notified about the question
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
                print 'Sending notification to %s with %d questions.' % (user, len(email_questions))

                send_template_email([user], notifications_template, {
                    'questions': email_questions,
                }, nodes=email_questions)





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
    today = datetime.today() #checked again and this still does not work for me
    time_delta = today - question.added_at 

    if (time_delta < timedelta(days =7)): # 1 week
        score = 5
    elif (time_delta < timedelta(days =30)): # 1 month
        score = 4
    elif (time_delta < timedelta(days =90)):
        score = 3
    elif (time_delta < timedelta(days =180)):
        score =2
    else:
        score = 1

    return score

def calculate_need(question):
    number_of_answers = Answer.objects.filter(parent=question).count()
    if (number_of_answers < 1): 
        score_boost = 5 
    elif (number_of_answers < 2): 
        score_boost = 3
    elif (number_of_answers < 3):
        score_boost = 2
    else:
        score_boost = 1
    return score_boost

def calculate_popularity(question):
    question_views = question.extra_count
    if(question_views > 1000): 
        score = 5
    elif(question_views > 500):
        score = 4
    elif(question_views > 250):
        score = 3
    elif(question_views > 125):
        score = 2
    elif(question_views > 50):
        score = 1
    else:
        score = 0

    return score

def interacted_before(user, question):
    students_questions = Question.objects.filter(author=question.author)
    if students_questions.filter(children__author=user).count() > 0:
        interacted_score = 5
    else:
        interacted_score = 0
    return interacted_score



#############################################
# Define matchable universe of items
#############################################

def get_valid_questions():
    today = datetime.today() 
    earliest_valid_date = today -timedelta(weeks = (52/12*9))
    q = (Question.objects
        .filter_state(deleted=False, closed=False)
        .filter(added_at__gt=earliest_valid_date)
        # Django gets strange when you filter before annotating
        .filter(children__node_type='answer') # Exclude comments 
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
