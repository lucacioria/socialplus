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
                # UPDATE
                pass
        
        if is_init:
            for p in with_circle:
                p.create_circle(self)
        elif self.needs_update():
            for p in with_circle:
            pass
        # UPDATE OR CREATE+LINK CIRCLES:
        # for each in with_circle:
        # check if circle is linked, if not create it and link it with Key and CircleID
        # also check if it needs to be removed/unlinked from anyone
        # then Step 2 = update the circle according to in_circle
        
        # check if the circle needs to be updated (self.needs_update)
        # return if false, continue if true
        # circle needs update = update existing circles, add/remove for deleted/new people
        
        # call update for each person in with_person
        # arg = self.key --> so person update knows which circle to update on g+
        # set to false after update