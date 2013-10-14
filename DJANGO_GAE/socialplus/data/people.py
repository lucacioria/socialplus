import logging
import json
import datetime

from google.appengine.ext import ndb

from socialplus.utils import *
from socialplus.data.tags import Tag

class User(ndb.Model):
    full_name        = ndb.StringProperty()
    primary_email    = ndb.StringProperty()

class TagReport(ndb.Model):
    tag             = ndb.KeyProperty(kind=Tag)
    count           = ndb.IntegerProperty(default=0)

class Person(ndb.Model):
    display_name     = ndb.StringProperty()
    image_url        = ndb.StringProperty()
    user             = ndb.KeyProperty(kind=User)
    user_primary_email = ndb.StringProperty() # redundant data for efficiency
    """internal properties"""
    tags    = ndb.StructuredProperty(TagReport, repeated=True)
    activities_last_updated = ndb.DateTimeProperty()

    def to_json(self):
        return format_json(self.to_dict_for_json())

    def to_dict_for_json(self):
        p = self.to_dict_with_id()
        del p["activities_last_updated"]
        p["google_id"] = self.key.id()
        p["user"] = p["user"].get().to_dict()
        for tag_report in p["tags"]:
            tag = tag_report["tag"].get().to_dict_with_id()
            del tag_report["tag"]
            tag_report["name"] = tag["name"]
            tag_report["id"] = tag["id"]
        return p

def save_person(p, user):
    old_p_ = ndb.Key(Person, p["id"], parent=user.key).get()

    # update existing person
    if old_p_:
        old_p_.display_name = p["displayName"]
        old_p_.image_url = p["image"]["url"]
        old_p_.user_primary_email = user.primary_email
        old_p_.put()
        return old_p_.key
    # create new person
    else:
        p_ = Person(parent=user.key, id=p["id"])
        p_.display_name = p["displayName"]
        p_.image_url = p["image"]["url"]
        p_.user_primary_email = user.primary_email
        p_.user = user.key
        return p_.put()

def save_user(u):
    old_u_ = ndb.Key(User, u["id"]).get()

    # update existing person
    if old_u_:
        old_u_.full_name = u["name"]["fullName"]
        old_u_.put()
        return old_u_.key
    # create new person
    else:
        u_ = User(parent=ndb.Key(User, u["id"]), id=u["id"])
        u_.full_name = u["name"]["fullName"]
        u_.primary_email = u["primaryEmail"]
        return u_.put()