# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *

from socialplus.api import create_plus_service, DOMAIN_NAME
from socialplus.routines import update_progress, mark_as_completed
from socialplus.data.people import User, save_person
from socialplus.data.domain import Domain

from google.appengine.api import search
from google.appengine.ext import ndb

def _sync_person_profile(user):
    plus = create_plus_service(user.primary_email)
    statistics = {
        "is_person": False,
    }
    # update user profile
    try:
        person_api = plus.people().get(userId=user.primary_email).execute()
    except: #todo restrict to right exception HttpError 404 dove cazzo si importa
        return statistics
    person = save_person(person_api, user)
    statistics["is_person"] = True
    return statistics

def sync_people(sync_task):
    statistics = {
        "total_users": 0,
        "total_people": 0,
    }
    # get domain for progress reasons (know total num of users)
    domain = ndb.Key(Domain,"main").get()
    # batch size of user fetch
    batch_size = 10
    update_progress(sync_task, "\nstarting update of all Domain users G+ profiles..\n", 0, 100)
    n = 0
    while True:
        q = User.query().fetch(limit=batch_size, offset=n*batch_size)
        for user in q:
            statistics["total_users"] += 1
            person_statistics = _sync_person_profile(user)
            if person_statistics["is_person"]:
                statistics["total_people"] += 1
                update_progress(sync_task, user.primary_email + ", ", statistics["total_users"], domain.user_count)
            else:
                update_progress(sync_task, ".", statistics["total_users"], domain.user_count)
        if len(q) == batch_size:
            n += 1
        else:
            break
    mark_as_completed(sync_task, "\n" + str(statistics["total_people"]) + " user profiles synced, out of " + \
        str(statistics["total_users"]) + " users in the domain\n")
    domain.person_count = statistics["total_people"]
    domain.put()
