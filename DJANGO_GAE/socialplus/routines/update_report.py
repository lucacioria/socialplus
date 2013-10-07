# -*- coding: UTF-8 -*-
import httplib2
import json
import logging
import pprint
import datetime

from socialplus.utils import *
from socialplus.data.activities import Activity, search_activities_paginated, get_activities
from socialplus.views import search_activities
from socialplus.routines import update_progress, mark_as_completed

from google.appengine.ext import ndb
from google.appengine.api import search

def update_report(task):
    # retrieve report object from datastore
    key = ndb.Key(urlsafe=task.update_report_report_id)
    report = key.get()
    # update report timestamp
    report.last_updated = datetime.datetime.now()
    # reset report data
    report.reset_data()
    # prepare for search api
    page_size = 100
    cursor = search.Cursor()
    update_progress(task, "\nstarting update of report " + report.name + "..\n", 0, 100)
    while True:
        # search api call, paginated
        ids, cursor = search_activities_paginated(report.search_string, cursor=cursor, limit=page_size)
        # exit loop if no activities were found
        if len(ids) == 0: break
        # get ndb entities
        activities = get_activities(ids)
        # loop over activities and perform report updates
        for a in activities:
            report.update_with_activity(a)
        # exit if no more activities form search api
        if cursor == None:
            break
    update_progress(task, "\nfinishing..\n", 0, 100)
    # sort repeated interval properties (by day, by month, by year)
    report.data_by_day.sort(key = lambda x: x.interval)
    report.data_by_month.sort(key = lambda x: x.interval)
    report.data_by_year.sort(key = lambda x: x.interval)
    # sort and trim active users
    def sort_and_trim(rd):
        rd.active_people.sort(key = lambda x: -x.total)
        del rd.active_people[3:]
    sort_and_trim(report.data_ever)
    map(sort_and_trim, report.data_by_day)
    map(sort_and_trim, report.data_by_month)
    map(sort_and_trim, report.data_by_year)
    # save updated report to datastore
    report.put()
    # return report as json
    mark_as_completed(task, "\nreport updated\n")
    