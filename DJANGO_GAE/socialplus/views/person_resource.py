import json
import logging
import datetime

from django.http import HttpResponse

from socialplus.utils import *
from socialplus.data.people import Person
from authorized_decorator import authorized

from google.appengine.ext import ndb

@authorized
def get_person(request, id_):
    person = ndb.Key(urlsafe=id_).get()
    return HttpResponse(person.to_json())

@authorized
def get_people(request):
    people = [x.to_dict_for_json_light() for x in Person.query().fetch(9999)]
    return HttpResponse(format_json({"items": people}))