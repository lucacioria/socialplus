import json
import logging
from datetime import date, datetime

from django.http import HttpResponse

from socialplus.utils import *
from socialplus.data.reports import *

from google.appengine.api import search
from google.appengine.ext import ndb

def create_report(request):
    # get POST request data
    data = json.loads(request.body)
    # check if name is taken
    key = ndb.Key(Report, data["name"], parent=ndb.Key("Domain", "main"))
    if key.get() != None:
        return HttpResponse("Report name already exists", status=422)
    # create ndb entity
    report = Report(key=key)
    report.name = data["name"]
    report.search_string = data["searchString"]
    # initialize report data to default values
    report.reset_data()
    # save to datastore
    report.put()
    # return report without data (which is empy now)
    return HttpResponse(report.to_json_light(), status=201)

def delete_report(request, reportId):
    # retrieve report object from datastore
    key = ndb.Key(urlsafe=reportId)
    report = key.delete()
    return HttpResponse(status=204)

def get_report(request, reportId):
    # retrieve Report object from datastore
    key = ndb.Key(urlsafe=reportId)
    report = key.get()
    # return report
    return HttpResponse(report.to_json())

def get_reports(request):
    reports = [x.to_dict_for_json_light() for x in Report.query().fetch(9999)]
    return HttpResponse(format_json({"items": reports}))

def get_post_reports(request):
    if request.method == "GET":
        return get_reports(request)
    elif request.method == "POST":
        return create_report(request)
    else:
        raise Exception("illegal HTTP verb")

def get_delete_report(request, reportId):
    if request.method == "GET":
        return get_report(request, reportId)
    elif request.method == "DELETE":
        return delete_report(request, reportId)
    else:
        raise Exception("illegal HTTP verb")