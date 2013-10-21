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
    allow_add               = ndb.BooleanProperty(default=True)
    allow_remove            = ndb.BooleanProperty(default=False)
    last_gplus_update       = ndb.DateTimeProperty(auto_now=True)
    
    def __init__(self, n, inc, wc):
        self.name = n
        self.in_circle = inc
        self.with_circle = wc
        self.update(True)
        return self.put()
    
    @classmethod
    def get_by_name(cls, name):
        q = cls.query(cls.name==name)
        return q.get()
    
    def get_in_circle_list(self):
        list = []
        for ent in self.in_circle:
            if not isinstance(ent, CirclePerson):
                for x in ent.people:
                    list.append(x.key)
            else:
                list.append(ent.key)
        return list
    
    def needs_update(self):
        for s in in_circle:
            if s.has_changed == True:
                return True
        for t in with_circle:
            if t.has_changed == True:
                return True
        return False
    
    def add_to_in_circle(self, circle_input):
        self.in_circle.append(circle_input)
        return self.put()
    
    def add_to_with_circle(self, circle_input):
        self.with_circle.append(circle_input)
        return self.put()
    
    # UPDATES G+ CIRCLES
    # (domain sync is a background task: sync_circles::sync_gapps)
    def update(self, is_init=False):
        for p in self.with_circle:
            ent = p.get()
            if is_init:
                if not isinstance(ent, CirclePerson):
                    for x in ent.people:
                        x.get().create_circle(self)
                else:
                    ent.create_circle(self)
            elif self.needs_update():
                if not isinstance(ent, CirclePerson):
                    for rem in ent.removed_people:
                        rem.get().delete_circle(self)
                    for add in ent.added_people:
                        add.get().create_circle(self)
                    for people in ent.people:
                        people.get().update_circle(self)
                else:
                    if ent.has_circle(self):
                        ent.update_circle(self)
                    else:
                        ent.create_circle(self)