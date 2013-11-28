# -*- coding: UTF-8 -*-
import httplib2
import json
import logging
import datetime

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_plus_service

from socialplus.data.activities import save_activity
from socialplus.data.people import Person
from socialplus.routines import update_progress, mark_as_completed

from google.appengine.api import search
from google.appengine.ext import ndb

def _sync_person_activities(person, days):
    today = datetime.datetime.now()
    # authenticate
    plus = create_plus_service(person.user.get().primary_email)
    # statistics
    statistics = {
        "total_activities": 0,
    }
    # get activities from api
    avg_number_of_activities_per_month = 15
    max_results = min(50, max(5, int(days / 30.0 * avg_number_of_activities_per_month)))
    user_id = person.key.id()
    next_page_token = None
    activities = []
    # start requests
    keep_querying = True
    while keep_querying:
        request = plus.activities().list(userId=user_id, collection="user",\
                    maxResults=max_results, pageToken=next_page_token)
        activities_api = call_with_exp_backoff(request)
        # break if empty list
        if len(activities_api["items"]) == 0: break
        # add activities published less than 'days' ago
        for a in activities_api['items']:
            if (today - str_to_datetime(a["published"])).days < days:
                activities.append(a)
            else:
                keep_querying = False
                break
        # get next page if needed
        if keep_querying and 'nextPageToken' in activities_api:
            next_page_token = activities_api['nextPageToken']
        else:
            break
    # get people shared to for each activity and save it
    for a in activities:
        request = plus.people().listByActivity(activityId=a["id"], collection="sharedto", fields="totalItems")
        sharedto = call_with_exp_backoff(request)
        save_activity(a, sharedto, person.key)
        statistics["total_activities"] += 1
    return statistics

def sync_activities(task):
    statistics = {
        "total_activities": 0,
        "total_people": 0,
    }
    # how many days back to sync
    days = 9999 # syncs all activities
    if task.sync_activities_days:
        days = task.sync_activities_days
    #
    if task.sync_activities_person_email:
        update_progress(task, \
            "\nstarting update for selected person..\n", 0, 100)
        person = Person.query(Person.user_primary_email==task.sync_activities_person_email).get()
        if person:
            _sync_person_activities(person, days)
            mark_as_completed(task, "\nfinished update for " + person.display_name)
        else:
            mark_as_completed(task, "\nFAILED update for " + person.display_name)
    else:
        update_progress(task, \
            "\nstarting update of all activities for people in Domain..\n", 0, 100)
        q = Person.query().fetch(9999)
        for person in q:
            statistics["total_people"] += 1
            person_statistics = _sync_person_activities(person, days)
            statistics["total_activities"] += person_statistics["total_activities"]
            update_progress(task, person.display_name + " (" + str(person_statistics["total_activities"]) + " activities), ", statistics["total_people"], len(q))
        mark_as_completed(task, "\n" + str(statistics["total_people"]) + " people, with " + str(statistics["total_activities"]) + " total activities")