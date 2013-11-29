# -*- coding: UTF-8 -*-
import httplib2
import json
import logging
import traceback

from socialplus.utils import *

from socialplus.api import create_plus_service
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
        request = plus.people().get(userId=user.primary_email)
        person_api = call_with_exp_backoff(request)
    except:
        logging.error("Error fetch person %s : %s" % (user.primary_email, traceback.format_exc()))
        return statistics
    person = save_person(person_api, user)
    statistics["is_person"] = True
    return statistics

def sync_people(task):
    statistics = {
        "total_users": 0,
        "total_people": 0,
    }
    # get domain for progress reasons (know total num of users)
    domain = ndb.Key(Domain,"main").get()
    # batch size of user fetch
    batch_size = 10
    update_progress(task, "\nstarting update of all Domain users G+ profiles..\n", 0, 100)
    n = 0
    while True:
        if task.sync_people_org_unit_path != None and len(task.sync_people_org_unit_path) > 0:
            q = User.query(User.org_unit_path==task.sync_people_org_unit_path).fetch(limit=batch_size, offset=n*batch_size)
        else:
            q = User.query().fetch(limit=batch_size, offset=n*batch_size)
        for user in q:
            statistics["total_users"] += 1
            person_statistics = _sync_person_profile(user)
            if person_statistics["is_person"]:
                statistics["total_people"] += 1
                update_progress(task, user.primary_email + ", ", statistics["total_users"], domain.user_count)
            else:
                update_progress(task, ".", statistics["total_users"], domain.user_count)
        if len(q) == batch_size:
            n += 1
        else:
            break
    mark_as_completed(task, "\n" + str(statistics["total_people"]) + " user profiles synced, out of " + \
        str(statistics["total_users"]) + " users in the domain\n")
    domain.person_count = statistics["total_people"]
    domain.put()
