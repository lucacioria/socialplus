# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.data.activities import Activity, save_activity_search_document, delete_search_index
from socialplus.routines import update_progress, mark_as_completed

from google.appengine.ext import ndb

def update_search_index(task):
    statistics = {
        "total_documents": 0,
    }
    # delete the current index
    delete_search_index()
    # rebuild the index
    update_progress(task, \
        "\nstarting update of search indices for all profiles and activities..\n", 0, 9999)
    q = Activity.query().fetch(9999) #todo scale to more activities
    for activity in q:
        save_activity_search_document(activity)
        statistics["total_documents"] += 1
        # update_progress(task, "", statistics["total_documents"], len(q))

    mark_as_completed(task, "\n" + str(statistics["total_documents"]) + " documents synced\n")
