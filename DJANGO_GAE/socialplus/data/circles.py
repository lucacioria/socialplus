import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search

from socialplus.data import *
from socialplus.data.circlesources import *
from socialplus.utils import *
from socialplus.api import * 


class Circle(ndb.Model):
    name                    = ndb.StringProperty(required=True) # needs to be unique
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
        self.update(True)
    
    @classmethod
    def get_by_name(cls, name):
        q = cls.query(cls.name==name)
        return q.get()
    
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
    def update(self, is_init=False):
        for p in self.with_circle:
            if is_init:
                p.create_circle(self)
            elif self.needs_update():
                if not isinstance(p, CirclePerson) and p.removed_people:
                    for rem in p.removed_people:
                        
                p.update_circle(self)