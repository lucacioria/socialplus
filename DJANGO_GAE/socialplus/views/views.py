import httplib2
import logging

from socialplus.data.activities import Activity
from socialplus.data.domain import Domain
from socialplus.data.people import Person, User
from socialplus.data.tasks import Task
from socialplus.utils import *

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from google.appengine.ext import ndb

@ensure_csrf_cookie
def get_cookie(request):
    return HttpResponse("this GET is to set the CSRF cookie")

def get_communities(request):
    q = Activity.query(projection=["access.community_name"], distinct=True).fetch(999)
    q = [x.access.community_name for x in q if x.access.community_name is not None]
    print q
    return HttpResponse(format_json({"items": [{"name" : x} for x in q]}))

def reset_domain(request):
    domain = Domain(id="main")
    domain.put()
    return HttpResponse("domain reset")

def delete_reports(request):
    ndb.delete_multi(Report.query().fetch(999999, keys_only=True))
    return HttpResponse("all reports deleted")

def delete_tasks(request):
    ndb.delete_multi(Task.query().fetch(999999, keys_only=True))
    return HttpResponse("all reports tasks")


def delete_people(request):
    ndb.delete_multi(Person.query().fetch(999999, keys_only=True))
    delete_activities(request)
    return HttpResponse("all people and activities deleted")

def delete_users(request):
    ndb.delete_multi(User.query().fetch(999999, keys_only=True))
    delete_people(request)
    return HttpResponse("all users, people and activities deleted")

def delete_activities(request):
    ndb.delete_multi(Activity.query().fetch(999999, keys_only=True))
    return HttpResponse("all activities deleted")