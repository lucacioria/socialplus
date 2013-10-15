import logging
import json
import datetime
from pprint import pprint


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
    circle_name         = ndb.StringProperty(required=True)

class CirclePerson(CircleInput):
    email               = ndb.StringProperty(required=True)
    has_gplus           = ndb.BooleanProperty(default=False)
    gplus_id            = ndb.StringProperty()
    circles             = ndb.StructuredProperty(CircleID, repeated=True)
    people_count        = ndb.ComputedProperty(lambda e: len(e.circles))
    orgUnitPath         = ndb.StringProperty()
    
    @classmethod
    def find_or_create(cls, email, orgUnitPath=None):
        q = cls.query(cls.email==email)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(email=email,orgUnitPath=orgUnitPath)
        ent.check_has_gplus()
        ent.put()
        print("creating entity")
        return (ent, True)
    
    @classmethod
    def find_and_delete(cls, email):
        q = cls.query(cls.email==email)
        ent = q.get()
        if ent is None:
            return False
        ent.key.delete()
        return True
    
    def people(self):
        return self
    
    #@TODO: FIX
    def check_has_gplus(self):
        if not self.has_gplus:
            try:
                print("entering plus check")
                plus            = create_plus_service(self.email)
                people          = plus.people()
                # pprint(people)
                result          = people.get(userId="me").execute()
                # pprint(result)
                # @TODO
                # Exception: <HttpError 401 when requesting https://www.googleapis.com/plus/v1domains/people/me?alt=json returned "Invalid Credentials">
                self.has_gplus  = "kind" in result # or: result not None ?
            except Exception as e:
                print "Exception: "+format(str(e))
    
    def create_circle(self, circle):
        plus            = create_plus_service(self.email)
        circle          = plus.circles().insert(userId="me", body={'displayName': circle.name}).execute()
        circle_id       = circle.get('id')
        self.circles.append(CircleID.new(circle_id=circle_id, circle_name=circle.name))
        for source in circle.in_circle:
            for pin in source.people():
                result = plus.circles().addPeople(circleId=circle_id, email=pin.email).execute()


    def update_circle(self, circle):
        # first: update all circles (add/remove), if in_circle has changed
        # then: update who has the circle (add/remove), if with_circle has changed
        pass




class OrgUnit(CircleInput):
    name                = ndb.StringProperty(required=True)
    orgUnitPath         = ndb.StringProperty(required=True)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    people_count        = ndb.ComputedProperty(lambda e: len(e.people))
    
    @classmethod
    def find_or_create(cls, name, orgUnitPath):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(name=name, orgUnitPath=orgUnitPath)
        ent.put()
        return (ent, True)
    
    # move these into a base class ...
    @classmethod
    def get_list(cls):
        return [ou.name for ou in cls.query().fetch(9999)]
    
    @classmethod
    def find_and_delete(cls, name):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is None:
            return False
        ent.key.delete()
        return True
    
    def update_from_source(self):
        if not self.people:
            users = CirclePerson.query(CirclePerson.orgUnitPath == self.orgUnitPath).fetch(9999)
            self.people = [x.key for x in users]
        else:
            # THIS updates self.people (NOT existence of orgUnit)
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
    people_count        = ndb.ComputedProperty(lambda e: len(e.people))
    
    @classmethod
    def find_or_create(cls, name, group_email):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(name=name, group_email=group_email)
        ent.put()
        return (ent, True)
    
    def update_from_source(self):
        if not self.people:
            directory = create_directory_service()
            members = directory.members().list(groupKey=self.group_email, maxResults=1000).execute()
            print("MEMBERS: ")
            pprint(members)
            people_keys = []
            while True:
                if "members" in members:
                    for member in members["members"]:
                        if "email" in member:
                            p = CirclePerson.find_or_create(member["email"])[0]
                            people_keys.append(p.key)
                if "pageToken" in members:
                    members = directory.members().list(groupKey=self.group_email, maxResults=1000, pageToken=members["pageToken"]).execute()
                else:
                    break
            self.people = people_keys
            self.put()
        else:
            # THIS updates self.people (NOT existence of Group)
            self.set_updated()
            # UPDATE