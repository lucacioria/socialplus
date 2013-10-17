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
from google.appengine.api import search

@ensure_csrf_cookie
def get_cookie(request):
    return HttpResponse("this GET is to set the CSRF cookie")

def get_communities(request):
    q = Activity.query(projection=["access.community_name"], distinct=True).fetch(9999)
    q = [x.access.community_name for x in q if x.access.community_name is not None]
    print q
    return HttpResponse(format_json({"items": [{"name" : x} for x in q]}))

def get_providers(request):
    q = Activity.query(projection=["provider"], distinct=True).fetch(9999)
    q = [x.provider for x in q if x.provider is not None]
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

def delete_activities_search_index(request):
    doc_index = search.Index(name="activities")
    # looping because get_range by default returns up to 100 documents at a time
    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
        # Delete the documents for the given ids from the Index.
        doc_index.delete(document_ids)
    return HttpResponse("all activities removed from search index")