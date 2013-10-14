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
    has_changed         = ndb.BooleanProperty(default=False)
    last_update         = ndb.DateTimeProperty(auto_now=True)
    
    def set_updated(self):
        self.has_changed = False
        return self.put()
    
class CircleID(ndb.Model):
    circle_id           = ndb.StringProperty(default="", required=True)
    circle              = ndb.KeyProperty(kind=Circle)

class OrgUnit(CircleInput):
    name                = ndb.StringProperty(required=True)
    orgUnitPath         = ndb.StringProperty(required=True)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    
    @classmethod
    def find_or_create(cls, name, orgUnitPath):
        obj         = cls.query(cls.name==name)
        if obj is None:
            obj     = cls.new(name=name, orgUnitPath=orgUnitPath)
        return obj
    
    def update_from_source(self):
        if not self.people:        
            users = CirclePerson.query(CirclePerson.orgUnitPath=orgunit["orgUnitPath"])
            self.people = ndb.put_multi_async([x in users])  # is this equivalent to [x.key for x in users] ?
        else:
            # reset updated prior to update
            self.set_updated()
            # check if orgUnit still exists
            directory = create_directory_service()
            exist = directory.orgunits().get(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"], orgUnitPath=self.orgUnitPath).execute()
            if not exist: return self.key.delete()
            # it still exists, update the people in it
            
            
            
            # we assume Person Sync has run previously
            # check diff between matching (orgUnitPath) CirclePerson object
            # update self.people list of Keys accordingly (add/remove)
            # if anything changed set has_changed = True
            
            # if changed, update set needs_update=true for Circles that contain self
            # --> Circle.query( in_circles or with_circles )
        
    
class Group(CircleInput):
    name                = ndb.StringProperty(required=True)
    group_email         = ndb.StringProperty(required=True)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    
    @classmethod
    def find_or_create(cls, name, group_email):
        obj         = cls.query(cls.name==name)
        if obj is None:
            obj     = cls.new(name=name, group_email=group_email)
        return obj
    
    def update_from_source(self):
        if not self.people:
            members = directory.members().list(group["email"], maxResults=1000).execute()
            people = []
            while True:
                for member in members["members"]:
                    people.append(CirclePerson.find_or_create(member["email"]))
                if members["pageToken"]:
                    members = directory.members().list(group["email"], maxResults=1000, pageToken=members["pageToken"]).execute()
                else:
                    break
            self.people = ndb.put_multi_async([x in people])
        else:
            self.set_updated()
            # UPDATE
    
    
class CirclePerson(CircleInput):
    email               = ndb.StringProperty(required=True)
    has_gplus           = ndb.BooleanProperty(default=False)
    gplus_id            = ndb.StringProperty()
    circles             = ndb.StructuredProperty(CircleID, repeated=True) # CirclePerson needs to know about its Circles (CircleID) in order to update them
    orgUnitPath         = ndb.StringProperty()
    
    def __init__(self, email, orgUnitPath=None):
        self.email          = email
        self.orgUnitPath    = orgUnitPath
        self.check_has_gplus()
    
    @classmethod
    def find_or_create(cls, email, orgUnitPath=None):
        obj         = cls.query(cls.email==email)
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
    
    def create_circle(self, circle):
        plus            = create_plus_service(self.email)
        circle          = plus.circles().insert(userId="me", body={'displayName': circle.name}).execute()
        circle_id       = circle.get('id')
        self.circles.append(CircleID.new(circle_id=circle_id, circle=circle.key))
        for source in circle.in_circle:
            for pin in source.people():
                result = plus.circles().addPeople(circleId=circle_id, email=pin.email).execute()
        
    
    def update_circle(self, circle):
        # first: update all circles (add/remove), if in_circle has changed
        # then: update who has the circle (add/remove), if with_circle has changed
        
    
    
    
    
    
    
    
    
    