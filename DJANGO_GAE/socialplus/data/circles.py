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
    
    def __init__(self, name, inc, wc):
        super(Circle, self).__init__()
        self.name = name
        self.in_circle = inc
        self.with_circle = wc
        # self.create_circle() # needs to be called manually
        self.put()
    
    @classmethod
    def get_by_name(cls, name):
        q = cls.query(cls.name==name)
        return q.get()
    
    @classmethod
    def find_or_create(cls, name, inc, wc):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(name, inc, wc)
        return (ent, True)
    
    def get_in_circle_list(self):
        list = []
        for ent in self.in_circle:
            for x in ent.people:
                list.append(x.key)
        return list
    
    def needs_update_in_circle(self):
        for s in in_circle:
            if s.has_changed == True:
                return True
        return False
    
    # @returns: True if the Circle has been added/removed FOR a person
    def needs_update_with_circle(self):
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
    
    # first creates the circle for people in self.people
    def create_circle(self):
        for ent in [p.get() for p in self.with_circle]:
            for x in ent.people:
                x.get().create_circle(self)
            else:
                ent.create_circle(self)
    
    # This creates/removes the Circle from people in self.with_circle
    def update_with_circle(self):
        if not self.needs_update_with_circle(): return False
        for p in self.with_circle:
            if not isinstance(ent, CirclePerson):
                for rem in ent.removed_people:
                    rem.get().delete_circle(self)
                for add in ent.added_people:
                    add.get().create_circle(self)