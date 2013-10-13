import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search

from socialplus.data import *
from socialplus.utils import *
from socialplus.api import * 


class Circle(ndb.Model):
    name                    = ndb.StringProperty(required=True)
    in_circle               = ndb.KeyProperty(kind=CircleInput, repeated=True)
    with_circle             = ndb.KeyProperty(kind=CircleInput, repeated=True)
    enforce_exist           = ndb.BooleanProperty(default=True)
    allow_add               = ndb.BooleanProperty(default=False)
    allow_remove            = ndb.BooleanProperty(default=False)
    # needs_update            = ndb.BooleanProperty(default=True)
    last_gplus_update       = ndb.DateTimeProperty(auto_now=True)
    
    def __init__(self, name, in_circle=[], with_circle=[]):
        self.name = name
        self.in_circle = in_circle
        self.with_circle = with_circle
        self.update()
    
    def needs_update(self):
        for s in in_circle:
            if s.has_changed == True:
                return True
        for t in with_circle:
            if t.has_changed == True:
                return True
        return False
    
    # UPDATES G+ CIRCLES
    # (domain sync is a background task: sync_circles::sync_gapps)
    def update(self):
        # check_domain updates: call update on all in_circle and with_circle
        # only update if circle needs_update==true
        # call update for each person in with_person
        # arg = self.key --> so person update knows which circle to update on g+
        # set to false after update
        for source in self.with_circle:
            # for each source.people, call this
            # update this circle for them
            
            
            
            