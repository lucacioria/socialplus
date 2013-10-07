import httplib2
import json
import logging
import pprint

from django.http import HttpResponse
from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_plus_service

from google.appengine.ext import ndb

def sync_auto_circle(circle):
    # for each user in emails_with_circle
    for email in [x.strip() for x in circle.emails_with_circle.split(",")]:
        # authenticate as user
        plus = create_plus_service(email)
        # search for circle with displayName = circle.name
        circles = plus.circles().list(userId=email).execute()
        old_circle = None
        for x in circles["items"]:
            if x["displayName"] == circle.name:
                old_circle = x
                print("found old circle: " + str(x))
        if old_circle != None:
            # delete it
            plus.circles().remove(circleId=old_circle["id"]).execute()
        # create a new one with same name
        new_circle = plus.circles().insert(userId = 'lucacioria@appseveryday.com', \
                body = {'displayName': circle.name}).execute()
        print("new circle: " + str(new_circle))
        # add people to the newly created circle
        plus.circles().addPeople(circleId=new_circle["id"], email=[x.strip() for x in circle.emails_in_circle.split(",")]).execute()

def sync_all_circles(request):
    auto_circles = AutoCircle.query().fetch(999)
    for circle in auto_circles:
        sync_auto_circle(circle)
    return HttpResponse("done")

def get_autocircles(request):
    from itertools import chain
    q = [dict(chain({"id_": x.key.urlsafe()}.items(), x.to_dict().items())) for x in AutoCircle.query().fetch(100)]
    return HttpResponse(format_json(q))

def delete_autocircle(request, autocircleId):
    # retrieve Autocircle object from datastore
    key = ndb.Key(urlsafe=autocircleId)
    autocircle = key.delete()
    return HttpResponse("autocircle deleted")

def create_autocircle(request):
    # retrieve Autocircle object from datastore
    new_autocircle = AutoCircle()
    new_autocircle.name = "NEW AUTOCIRCLE"
    new_autocircle.put()
    return HttpResponse("autocircle created")

def update_autocircle(request, autocircleId):
    # retrieve Autocircle object from datastore
    key = ndb.Key(urlsafe=autocircleId)
    # new data
    data = json.loads(request.body)
    print(format_json(data))
    autocircle = key.get()
    autocircle.name = data["name"]
    autocircle.emails_with_circle = data["emails_with_circle"]
    autocircle.emails_in_circle = data["emails_in_circle"]
    autocircle.put()
    # return confirmation
    return HttpResponse("autocircle updated")
