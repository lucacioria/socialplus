# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.api import create_directory_service, DOMAIN_NAME
from socialplus.routines import update_progress, mark_as_completed
from socialplus.data.people import save_user
from socialplus.data.domain import Domain

from google.appengine.api import search
from google.appengine.ext import ndb

def sync_users(task):
    directory = create_directory_service()

    statistics = {
        "total_users": 0,
    }
    update_progress(task, "\ncalling Directory API to update list of users..\n", 0, 100)
    update_progress(task, "starting update\n", 10, 100)
    users_api = directory.users().list(domain=DOMAIN_NAME).execute()
    while True:
        for user in users_api['users']:
            save_user(user)
            statistics["total_users"] += 1
        if 'nextPageToken' in users_api:
            update_progress(task, str(statistics["total_users"]) + " users updated\n", 30, 100)
            users_api = directory.users().list(domain=DOMAIN_NAME, pageToken=users_api['nextPageToken']).execute()
        else:
            break
    # update statistics in Domain entity
    domain = ndb.Key(Domain,"main").get()
    domain.user_count = statistics["total_users"]
    domain.put()
    # complete task
    mark_as_completed(task, str(statistics["total_users"]) + " users updated\n")