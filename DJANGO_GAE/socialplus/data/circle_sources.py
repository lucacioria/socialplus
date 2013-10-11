import logging
import json
import datetime

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import * 

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class CircleInput(polymodel.PolyModel):
    # abstract base class
    
class CircleID(ndb.Model):
    circle_id           = ndb.StringProperty(default="", required=True)
    circle              = ndb.KeyProperty(kind=Circle)

class OrgUnit(CircleInput):
    name                = ndb.StringProperty(required=True)
    orgUnitPath         = ndb.StringProperty(required=True)
    has_changed         = ndb.BooleanProperty(default=False)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    last_update         = ndb.DateTimeProperty(auto_now=True)
    
    def __init__(self, name):
        self.name       = name      
        
    
class Group(CircleInput):
    name                = ndb.StringProperty(required=True)
    group_email         = ndb.StringProperty(required=True)
    has_changed         = ndb.BooleanProperty(default=False)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    last_update         = ndb.DateTimeProperty(auto_now=True)
    
    
    
class CirclePerson(CircleInput):
    email               = ndb.StringProperty(required=True)
    has_gplus           = ndb.BooleanProperty(default=False)
    gplus_id            = ndb.StringProperty()
    circles             = ndb.StructuredProperty(CircleID, repeated=True)
    orgUnitPath         = ndb.StringProperty()
    last_update         = ndb.DateTimeProperty(auto_now=True)
    
    def __init__(self, email, orgUnitPath=None):
        self.email          = email
        self.orgUnitPath    = orgUnitPath
        self.check_has_gplus()
    
    @classmethod
    def find_or_create(cls, email, orgUnitPath=None):
        obj         = cls.query(CirclePerson.email==email)
        if obj is None:
            obj     = cls.new(email, orgUnitPath)
        return obj
    
    def people(self):
        return self
            
    
    def check_has_gplus(self):
        if not has_gplus:
            try:
                plus            = create_plus_service(self.email)
                results         = plus.people().search(maxResults=10, query=self.email).execute()
                self.has_gplus  = results["items"].count==1
            except Exception as e:
                print e
    
    def update_circles(self):
        # for each circle object in circles:
        # check if user has that circle (check circleId)
        # create the circle or update the circle
        
    
    
    
    
    
    
    
    
    