import json
import httplib2
import logging
import sys
import os

from django.http import HttpResponse

from google.appengine.ext import ndb
from google.appengine.api import search

from socialplus.utils import *
from socialplus.api import create_directory_service, create_plus_service
# from socialplus.data.reports import Report
from socialplus.data.tags import Tag
from socialplus.data.activities import Activity, save_activity, search_activities_paginated, get_activities, save_activity_search_document
from socialplus.data.people import User, save_user, Person, save_person, TagReport

def run_test(request, test_name):
    result, message = globals()["test_" + test_name]()
    out = ""
    if result:
        out += "<h2 style='color: green'>OK</h2>\n"
    else:
        out += "<h2 style='color: red'>FAIL</h2>\n"
    out += "<pre>" + message + "</pre>"
    return HttpResponse(out)

def test_users():
    user_id = "115139687869195831792" # lucacioria@appseveryday.com
    # delete all users
    _delete_users()
    # download user with api
    directory = create_directory_service()
    user_api = directory.users().get(userKey=user_id).execute()
    # save it to datastore
    user_key = save_user(user_api)
    user = user_key.get()
    # dump json representation and check it's good
    json = format_json(user.to_dict_with_id())
    return True, json

def test_people():
    user_id = "115139687869195831792" # lucacioria@appseveryday.com
    # delete all users and people
    _delete_users()
    _delete_people()
    _delete_tags()
    # download user with api
    directory = create_directory_service()
    user_api = directory.users().get(userKey=user_id).execute()
    # save it to datastore
    user_key = save_user(user_api)
    user = user_key.get()
    # download person from api
    plus = create_plus_service(user.primary_email)
    person_api = plus.people().get(userId=user.primary_email).execute()
    # save it to datastore
    person_key = save_person(person_api, user)
    person = person_key.get()
    # create a tag
    tag = Tag()
    tag.name = "nome"
    tag_key = tag.put()
    tag = tag_key.get()
    # add tagReport to person
    tag_report = TagReport()
    tag_report.tag = tag.key
    tag_report.count = 17
    person.tags = [tag_report]
    # dump json representation and check it's good
    json = person.to_json()
    return True, json

def test_tags():
    # create tag and put it
    tag = Tag()
    tag.name = "nome"
    tag.search_strings = ["ss1", "ss2"]
    tag_key = tag.put()
    tag = tag_key.get()
    # return json representation
    return True, tag.to_json()

def test_activities():
    _delete_activities()
    # define IDs of interesting activities
    activities = [
        {
            "id": "z12jc50azkfbyxy0e234tz35bwezjbzzq04",
            "shared": True,
            "restricted": False,
            "visibility": "private"
        },{
            "id": "z12hwb5wpmn1ddnpg04cgnbwgozlfxwzzys0k",
            "shared": False,
            "restricted": False,
            "visibility": "public"
        },{
            "id": "z13mgz0wezumshsyp04cgnbwgozlfxwzzys0k",
            "shared": False,
            "restricted": False,
            "visibility": "private"
        },{
            "id": "z12vhzgyetmcjpfdl234tz35bwezjbzzq04",
            "shared": False,
            "restricted": True,
            "visibility": "public"
        },{
            "id": "z12jstt5xsvgjtnra04cgnbwgozlfxwzzys0k",
            "shared": False,
            "restricted": False,
            "visibility": "community"
        },

    ]
    # this creates the person lucacioria (author of the activities)
    test_people()
    person_key = Person.query(ancestor=ndb.Key("Domain","main")).fetch(100)[0].key
    # create a tag to attach to the activities
    tag = Tag()
    tag.name = "nome"
    tag.search_strings = ["ss1", "ss2"]
    tag_key = tag.put()
    # get the activities
    plus = create_plus_service("lucacioria@appseveryday.com")
    json = ""
    for a in activities:
        # download activity from api
        a["obj"] = plus.activities().get(activityId=a["id"]).execute()
        # save it to datastore and check results
        activity_key = save_activity(a["obj"], person_key)
        activity = activity_key.get()
        activity.tags = [tag_key, tag_key]
        json += activity.to_json() + "\n\n"
        if a["shared"] and activity.verb != "share":
            return False, a["id"] + " shared activity has not verb 'shared'" + "\n\n" + json
        if a["restricted"] and not activity.access.domain_restricted:
            return False, a["id"] + " restricted activity is not domain_restricted" + "\n\n" + json
        if a["visibility"] != activity.access.visibility:
            return False, a["id"] + " visibility not correct" + "\n\n" + json
    # dump json representation and check it's good
    return True, json

def test_activity_search():
    delete_search_documents()
    # run test activities to populate datastore
    test_activities()
    # update search index
    q = Activity.query(ancestor=ndb.Key("Domain", "main")).fetch(100)
    for activity in q:
        save_activity_search_document(activity)
    # perform a search
    ids1, _ = search_activities_paginated('visibility:("community") content:("digame")')
    ids2, _ = search_activities_paginated('post')
    # get the matching activities, append json form
    json = format_json([x.to_dict_for_json() for x in get_activities(ids1 + ids2)])
    # dump json representation and check it's good
    return True, json

def _delete_users():
    ndb.delete_multi(User.query().fetch(999999, keys_only=True))

def _delete_activities():
    ndb.delete_multi(Activity.query().fetch(999999, keys_only=True))

# def _delete_reports():
#     ndb.delete_multi(Report.query().fetch(999999, keys_only=True))

def _delete_people():
    ndb.delete_multi(Person.query().fetch(999999, keys_only=True))

def _delete_tags():
    ndb.delete_multi(Tag.query().fetch(999999, keys_only=True))

def _delete_everything():
    _delete_users()
    _delete_people()
    _delete_tags()
    # _delete_reports()
    _delete_activities()

def delete_search_documents():
    index = search.Index(name="activities")
    try:
        while True:
            document_ids = [document.doc_id for document in index.get_range(ids_only=True)]
            if not document_ids:
                break
            index.delete(document_ids)
    except search.Error:
        logging.exception("Error removing documents:")