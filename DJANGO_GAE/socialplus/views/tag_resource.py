import json
import logging
import datetime as dt

from django.http import HttpResponse

from socialplus.utils import *
from socialplus.sync import *
from socialplus.data import *
from authorized_decorator import authorized

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

@authorized
def get_tags(request):
    from itertools import chain
    q = [dict(chain({"id_": x.key.urlsafe()}.items(), x.to_dict().items())) for x in Tag.query().fetch(100)]
    for a in q:
        a["search_strings"] = [{"value": x} for x in a["search_strings"]]
    return HttpResponse(format_json(q))

@authorized
def delete_tag(request, tagId):
    # retrieve Tag object from datastore
    key = ndb.Key(urlsafe=tagId)
    tag = key.delete()
    return HttpResponse("tag deleted")

@authorized
def create_tag(request):
    # retrieve Tag object from datastore
    new_tag = Tag()
    new_tag.name = "NEW TAG"
    new_tag.put()
    return HttpResponse("tag created")

@authorized
def update_tag(request, tagId):
    # retrieve Tag object from datastore
    key = ndb.Key(urlsafe=tagId)
    # new data
    data = json.loads(request.body)
    tag = key.get()
    tag.name = data["name"]
    tag.search_strings = [x["value"] for x in data["search_strings"]]
    tag.put()
    # return confirmation
    return HttpResponse("tag updated")

@authorized
def get_experts(request, tagId):
    # get tag key from datastore (get)
    tag_key = ndb.Key(urlsafe=tagId)
    # search for people with matching expert areas (single query)
    q = Person.query(Person.expert_areas.tag == tag_key).fetch(100)
    experts = [x.to_dict() for x in q]
    # for each person, get user, save relevant expert area level
    for e in experts:
        e["user"] = e["user"].get().to_dict()
        e["expert_level"] = [x for x in e["expert_areas"] if x["tag"] == tag_key][0]["level"]
    # order results based on expert_area.level DESC
    experts.sort(key=lambda x: x["expert_level"], reverse=True)
    # return person entities
    return HttpResponse(format_json(experts))
