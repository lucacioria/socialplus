# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_plus_service

from socialplus.data.activities import save_activity
from socialplus.data.people import Person
from socialplus.routines import update_progress, mark_as_completed

from google.appengine.api import search
from google.appengine.ext import ndb

def _sync_person_activities(person):
    plus = create_plus_service(person.user.get().primary_email)
    statistics = {
        "total_activities": 0,
    }
    activities_api = plus.activities().list(userId=person.key.id(), collection="user").execute()
    for a in activities_api["items"]:
        sharedto = plus.people().listByActivity(activityId=a["id"], collection="sharedto", fields="totalItems").execute()
        save_activity(a, sharedto, person.key)
        statistics["total_activities"] += 1
    return statistics

def sync_activities(task):
    statistics = {
        "total_activities": 0,
        "total_people": 0,
    }
    # task.sync_activities_person_email = "lucacioria@appseveryday.com"
    if task.sync_activities_person_email:
        update_progress(task, \
            "\nstarting update for selected person..\n", 0, 100)
        person = Person.query(Person.user_primary_email==task.sync_activities_person_email).get()
        if person:
            _sync_person_activities(person)
            mark_as_completed(task, "\nfinished update for " + person.display_name)
        else:
            mark_as_completed(task, "\nFAILED update for " + person.display_name)
    else:
        update_progress(task, \
            "\nstarting update of all activities for people in Domain..\n", 0, 100)
        q = Person.query().fetch(9999)
        for person in q:
            statistics["total_people"] += 1
            person_statistics = _sync_person_activities(person)
            statistics["total_activities"] += person_statistics["total_activities"]
            update_progress(task, person.display_name + " (" + str(person_statistics["total_activities"]) + " activities), ", statistics["total_people"], len(q))
        mark_as_completed(task, "\n" + str(statistics["total_people"]) + " people, with " + str(statistics["total_activities"]) + " total activities")