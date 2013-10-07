# -*- coding: UTF-8 -*-
import httplib2
import json
import logging
import pprint

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_plus_service, create_directory_service, DOMAIN_NAME

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

def sync_expert_areas(sync_task):
    statistics = {
        "total_tags_found": 0,
        "total_tagged_activities": 0,
    }
    update_progress(sync_task, "\nstarting tagging of activities..\n", 0, 100)
    # clean expert areas for all activities
    for a in Activity.query().fetch(1000):
        a.tags = []
        a.put()
    # get all tags
    q = Tag.query().fetch(1000)
    # loop over tags
    for tag in q:
        # loop over search strings
        statistics["total_tags_found"] += 1
        for search_string in tag.search_strings:
            # perform search, get list of ids
            cursor = search.Cursor()
            while True:
                ids, cursor = search_activities_paginated_(search_string)
                if len(ids) == 0:
                    break
                activities = Activity.query(Activity.id_.IN(ids)).fetch(100)
                # loop over ids, get activity
                for a in activities:
                    # update activity adding tag if not present
                    statistics["total_tagged_activities"] += 1
                    a.tags.append(tag.key)
                    a.put()
                if not cursor:
                    break
        update_progress(sync_task, "tagging for " + tag.name + "\n", statistics["total_tags_found"], len(q) * 2)
    # update people
    # clean expert areas for all people
    for p in Person.query().fetch(1000):
        p.expert_areas = []
        p.put()
    # loop over activities
    for a in Activity.query().fetch(1000):
        # get activity author (person)
        person = a.actor.person.get()
        # loop over tags
        for tag in a.tags:
            updated = False
            # check if expert area for tag already exists
            for ea in person.expert_areas:
                if ea.tag == tag:
                    ea.level += 1
                    person.put()
                    updated = True
                    break
            if updated == False:
                # create virgin ExpertArea
                new_expert_area = ExpertArea()
                new_expert_area.tag = tag
                new_expert_area.tag_name = tag.get().name
                new_expert_area.level = 1
                person.expert_areas.append(new_expert_area)
                person.put()
    # create new feed and push to GSA
    # feed, _ = get_gsa_feed_()
    # do_post_gsa(feed)
    # finish task
    mark_as_completed(sync_task, "\n" + str(statistics["total_tagged_activities"]) + " total activities tagged\n")