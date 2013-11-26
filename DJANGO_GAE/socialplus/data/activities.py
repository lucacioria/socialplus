import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError
from google.appengine.api import search

from socialplus.utils import *
from socialplus.data.tags import Tag
from socialplus.data.people import Person

class ActivityAccess(ndb.Model):
    """Models the acl of an activity"""
    visibility           = ndb.StringProperty(choices=["shared privately", "extended circles", "public", "domain", "private community", "public community", "restricted community"])
    community_name       = ndb.StringProperty()
    community_category   = ndb.StringProperty()
    domain_restricted    = ndb.BooleanProperty()

class ActivityObject(ndb.Model):
    """Models the object of an activity"""
    id_                 = ndb.StringProperty()
    content             = ndb.TextProperty()
    original_content    = ndb.TextProperty()
    plusones            = ndb.IntegerProperty()
    reshares            = ndb.IntegerProperty()
    url                 = ndb.TextProperty()
    type_               = ndb.StringProperty(choices=["activity", "note"])
    actor_id            = ndb.StringProperty()
    actor_display_name  = ndb.StringProperty()
    actor_image_url     = ndb.StringProperty()

class Activity(ndb.Model):
    """Models an individual Activity"""

    title           = ndb.TextProperty()
    url             = ndb.TextProperty()
    verb            = ndb.StringProperty(choices=["post", "share"])
    annotation      = ndb.TextProperty()
    provider        = ndb.StringProperty()

    published       = ndb.DateTimeProperty()

    access          = ndb.StructuredProperty(ActivityAccess)
    object_         = ndb.StructuredProperty(ActivityObject)
    actor           = ndb.KeyProperty(kind=Person)

    tags            = ndb.KeyProperty(kind=Tag, repeated=True)

    def to_json(self):
        return format_json(self.to_dict_for_json())

    def to_dict_for_json(self):
        a = self.to_dict_with_id()
        # add googleId
        a["google_id"] = self.key.id()
        # create actor from Person
        actor_person = a["actor"].get().to_dict_with_id()
        a["actor"] = {}
        a["actor"]["id"] = actor_person["id"]
        a["actor"]["display_name"] = actor_person["display_name"]
        a["actor"]["image_url"] = actor_person["image_url"]
        # object.actor
        a["object_"]["actor"] = {}
        a["object_"]["actor"]["id"] = a["object_"].pop("actor_id")
        a["object_"]["actor"]["display_name"] = a["object_"].pop("actor_display_name")
        a["object_"]["actor"]["image_url"] = a["object_"].pop("actor_image_url")
        # tags
        a["tags"] = list(set(a["tags"]))
        a["tags"] = [x.get().to_dict_with_id_light() for x in a["tags"]]
        return a

def save_activity_search_document(a):
    doc = search.Document(
        doc_id = a.key.urlsafe(),
        fields=[
            search.HtmlField(name='content', value=a.object_.content),
            search.DateField(name='published', value=a.published.date()),
            search.AtomField(name='visibility', value=a.access.visibility),
            search.AtomField(name='community', value=a.access.community_name),
            search.AtomField(name='provider', value=a.provider),
            search.AtomField(name='verb', value=a.verb),
            search.AtomField(name='author', value=a.actor.get().user.get().primary_email),
            search.AtomField(name='google_id', value=a.key.id()),
        ])
    try:
        index = search.Index(name="activities")
        index.put(doc)
    except search.Error:
        logging.exception('PUT of Activity Document FAILED')

def delete_search_index():
    doc_index = search.Index(name="activities")
    if doc_index == None: return
    # looping because get_range by default returns up to 100 documents at a time
    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
        # Delete the documents for the given ids from the Index.
        doc_index.delete(document_ids)

def _get_activity_access(a, sharedto):
    access = ActivityAccess()
    # set domain_restricted boolean value
    access.domain_restricted = a["access"].get("domainRestricted", False)
    #  
    def set_community(access, a):
        import re
        if not is_valid_utf8(a["access"]["description"]):
            logging.warning("(invalid UTF8) community name and category cannot be parsed for activity " + a["id"])
        ma = re.match(u"(?u)(.+) \((.+)\)", a["access"]["description"], re.UNICODE)
        if (ma):
            access.community_name = ma.group(1)
            access.community_category = ma.group(2)
        else:
            logging.warning("(malformed for regexp) community name and category cannot be parsed for activity " + a["id"])
    # set visibility
    access_items = a["access"].get("items")
    if sharedto["totalItems"] == 0: 
        if access_items != None: # community public
            val = access_items[0]["type"]
            if val == "public":
                access.visibility = "public community"
            else:
                raise Exception("ACL cannot be parsed for activity " + a["id"])
        else: # can be community private or community restricted
            if access.domain_restricted:
                access.visibility = "restricted community"
            else:
                access.visibility = "private community"
        set_community(access, a)
    else: # not in community
        if access_items != None: # can be public or extended circles, or domain iff restricted
            val = access_items[0]["type"]
            if val == "domain":
                access.visibility = "domain"
            if val == "extendedCircles":
                access.visibility = "extended circles"
            if val == "public":
                access.visibility = "public"
        else: # is privately shared, but can also be domain (if description is "Domain")
            if a["access"].get("description") == "Domain":
                access.visibility = "domain"
            else:
                access.visibility = "shared privately"
    return access    

def save_activity(a, sharedto, personKey):
    old_a_ = ndb.Key(Activity, a["id"], parent=personKey).get()

    # update existing activity
    if old_a_:
        return old_a_

    # create new activity
    a_ = Activity(parent=personKey, id=a["id"])
    a_.title        = a["title"]
    a_.url          = a["url"]
    try:
        a_.verb         = a["verb"]
    except BadValueError:
        logging.warning("unknown verb: " + a["verb"] + " for activity " + a["id"])
    a_.annotation   = a.get("annotation")
    a_.provider     = a["provider"].get("title")
    a_.published    = datetime.datetime.strptime(a["published"], '%Y-%m-%dT%H:%M:%S.%fZ')

    a_.access = _get_activity_access(a, sharedto)

    a_.actor = personKey

    object_ = ActivityObject()
    object_.id_ = a["object"].get("id")
    object_.type_ = a["object"]["objectType"]
    object_.original_content = a["object"].get("originalContent")
    object_.content = a["object"]["content"]
    object_.url = a["object"]["url"]
    object_.plusones = a["object"]["plusoners"]["totalItems"]
    object_.reshares = a["object"]["resharers"]["totalItems"]
    if "actor" in a["object"]:
        object_.actor_id = a["object"]["actor"]["id"]
        object_.actor_display_name = a["object"]["actor"]["displayName"]
        object_.actor_image_url = a["object"]["actor"]["image"]["url"]

    a_.object_      = object_

    return a_.put()

def get_activities(ids=[]):
    if not ids or len(ids) == 0:
        return []
    q = ndb.get_multi([ndb.Key(urlsafe=x) for x in ids])
    return q

def search_activities_paginated(query_string, cursor=search.Cursor(), limit=20):
    ids = []
    index = search.Index(name="activities")
    print "received query with cursor: " + str(cursor.web_safe_string)
    try:
        # build options and query
        options = search.QueryOptions(cursor=cursor, limit=limit)
        query = search.Query(query_string=query_string, options=options)

        # search at least once
        result = index.search(query)
        number_retrieved = len(result.results)
        cursor = result.cursor

        print "search api retreived " +str(number_retrieved) + " results, out of approx " + str(result.number_found)

        if number_retrieved > 0:
            for doc in result.results:
                ids.append(doc.doc_id)

        print "returning ids.length " +str(len(ids))

        return ids, cursor
    except search.Error:
        logging.exception('Search failed')