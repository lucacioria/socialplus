import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search

from socialplus.data import *
from socialplus.utils import *
from socialplus.api import * 


class Circle(ndb.Model):
    circle_id               = ndb.StringProperty(default="", required=True)
    name                    = ndb.StringProperty(required=True)
    in_circle               = ndb.KeyProperty(kind=CircleInput, repeated=True)
    with_circle             = ndb.KeyProperty(kind=CircleInput, repeated=True)
    enforce_exist           = ndb.BooleanProperty(default=True)
    allow_add               = ndb.BooleanProperty(default=False)
    allow_remove            = ndb.BooleanProperty(default=False)
    last_gplus_update       = ndb.DateTimeProperty(auto_now=True)
    
    def __init__(self, name, in_circle=[], with_circle=[]):
        self.name = name
        self.in_circle = in_circle
        self.with_circle = with_circle
        for person in self.with_circle.people:
            CirclePerson.find_or_create(person.email)
    
    def update(self):
        # call create_or_update for each person in with_circle