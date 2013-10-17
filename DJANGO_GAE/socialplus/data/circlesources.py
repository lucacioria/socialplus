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
    last_update         = ndb.DateTimeProperty(auto_now=True)
    
class CircleID(ndb.Model):
    circle_id           = ndb.StringProperty(default="", required=True)
    circle_name         = ndb.StringProperty(required=True)

class CirclePerson(CircleInput):
    email               = ndb.StringProperty(required=True)
    givenName           = ndb.StringProperty()
    familyName          = ndb.StringProperty()
    has_gplus           = ndb.BooleanProperty(default=True)
    gplus_id            = ndb.StringProperty()
    circles             = ndb.StructuredProperty(CircleID, repeated=True)
    circle_count        = ndb.ComputedProperty(lambda e: len(e.circles))
    orgUnitPath         = ndb.StringProperty()
    
    @classmethod
    def find_or_create(cls, email, orgUnitPath=None, givenName=None, familyName=None):
        q = cls.query(cls.email==email)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(email=email,orgUnitPath=orgUnitPath, givenName=givenName, familyName=familyName)
        ent.check_has_gplus()
        ent.put()
        return (ent, True)
    
    @classmethod
    def find_and_delete(cls, email):
        q = cls.query(cls.email==email)
        ent = q.get()
        if ent is None:
            return False
        for circle in ent.circles:
            ent.delete_circle(circle)
        ent.key.delete()
        return True
    
    @classmethod
    def find_by_name(cls, givenName, familyName):
        q = cls.queryn(cls.givenName=givenName, cls.familyName=familyName)
        ent = q.get()
        if ent is None:
            return False
        return ent
    
    def people(self):
        return self
    
    def check_has_gplus(self):
        if not self.has_gplus:
            plus = create_plus_service(self.email)
            has = plus.people().get("me")
            self.has_gplus = has["isPlusUser"]
            self.put()
        return self.has_gplus
    
    def has_circle(self, c):
        return not not CirclePerson.query(CirclePerson.circles.circle_name==c.name).get()
    
    def circle_is_online(self, c):
        if not self.has_circle(c):
            return False
        else:
            cref = CirclePerson.query(CirclePerson.circles.circle_name==c.name).get()
            circle_id = cref.circle_id
            plus = create_plus_service(self.email)
            try:
                return not not plus.circles.get(circleId=circle_id)
            except Exception, e:
                return False

    def create_circle(self, c):
        plus            = create_plus_service(self.email)
        circle          = plus.circles().insert(userId=self.email, body={'displayName': c.name}).execute()
        circle_id       = circle.get('id')
        self.circles.append(CircleID(circle_id=circle_id, circle_name=c.name))
        for source in circle.in_circle:
            for pin in source.people():
                result = plus.circles().addPeople(circleId=circle_id, email=pin.email).execute()
        self.put()

    def delete_circle(self, c):
        cref = CirclePerson.query(CirclePerson.circles.circle_name==c.name).get()
        circle_id = cref.circle_id
        try:
            plus = create_plus_service(self.email)
            plus.circles().remove(circleId=circle_id).execute()
        except Exception, e:
            print(str(e))
        cref.key.delete()

    def update_circle(self, c):
        plus = create_plus_service(self.email)
        cref = CirclePerson.query(CirclePerson.circles.circle_name==c.name).get()
        circle_id = cref.circle_id
        for inc in c.in_circle:
            if inc.has_changed:
                for add in inc.added_people:
                    plus.circles().addPeople(circleId=circle_id, email=add.email)
                for rem in inc.removed_people:
                    plus.circles().removePeople(circleId=circle_id, email=rem.email)
    
    def update_circle_with_policies(self, c):
        plus = create_plus_service(self.email)
        cref = CirclePerson.query(CirclePerson.circles.circle_name==c.name).get()
        circle_id = cref.circle_id
        plus_circle = plus.people().listByCircle(circleId=circle_id).execute()
        in_circle_user_added = []
        in_circle_user_removed = [x.get().email for x in c.get_in_circle_list()]
        if not (c.allow_add and c.allow_remove):
            for person in plus_circle["items"]:
                found = CirclePerson.find_by_name(person["name"]["givenName"], person["name"]["familyName"])
                if found: # Person is supposed to be in the circle
                    in_circle_user_removed.remove(found.key)
                else:
                    in_circle_user_added.append(person["id"])
            if not c.allow_add:
                for pid in in_circle_user_added:
                    plus.circles().removePeople(circleId=circle_id, userId=pid)
            if not c.allow_remove:
                for key in in_circle_user_removed:
                    plus.circles().addPeople(circleId=circle_id, email=key.get().email)
        if c.enforce_exist and not self.circle_is_online(c):
            self.delete_circle(c)
            self.create_circle(c)


class CircleContainer(CircleInput):
    name                = ndb.StringProperty(required=True)
    people              = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    people_count        = ndb.ComputedProperty(lambda e: len(e.people))
    has_changed         = ndb.BooleanProperty(default=False)
    added_people        = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    removed_people      = ndb.KeyProperty(kind=CirclePerson, repeated=True)
    
    @classmethod
    def get_list(cls):
        return [x.name for x in cls.query().fetch(9999)]
    
    @classmethod
    def find_and_delete(cls, name):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is None:
            return False
        ent.key.delete()
        return True
    
    def set_updated(self):
        self.has_changed = False
        ndb.delete_multi(self.added_people)
        ndb.delete_multi(self.removed_people)
        return self.put()

class OrgUnit(CircleContainer):
    orgUnitPath         = ndb.StringProperty(required=True)
    
    @classmethod
    def find_or_create(cls, name, orgUnitPath):
        q = cls.query(cls.name==name)
        ent = q.get()
        if ent is not None:
            return (ent, False)
        ent = cls(name=name, orgUnitPath=orgUnitPath)
        ent.put()
        return (ent, True)
    
    def update_from_source(self):
        users = CirclePerson.query(CirclePerson.orgUnitPath == self.orgUnitPath).fetch(9999)
        added = [x.key for x in users]
        if not self.people:
            self.people = added
            self.put()
        else:
            # reset self.has_changed
            self.set_updated()
            # check if orgUnit still exists
            try:
                directory = create_directory_service()
                exist = directory.orgunits().get(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"], orgUnitPath=self.orgUnitPath[1:]).execute()
                if not exist: return self.key.delete()
            except Exception, e:
                return self.key.delete()
            # update self.people, assuming previous sync_gapps_users() call
            removed = self.people
            intersection = list(set(added).intersection(set(removed)))
            added = list(set(added)-set(intersection))
            removed = list(set(removed)-set(intersection))
            if added or removed:
                self.has_changed = True
                for add in added:
                    self.people.append(add)
                    self.added_people.append(add)
                for rem in removed:
                    self.people.remove(rem)
                    self.removed_people.append(rem)
            self.put()
    
class Group(CircleContainer):
    group_email         = ndb.StringProperty(required=True)
    
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
        directory = create_directory_service()
        members = directory.members().list(groupKey=self.group_email, maxResults=1000).execute()
        added = []
        while True:
            if "members" in members:
                for member in members["members"]:
                    if "email" in member:
                        p = CirclePerson.find_or_create(member["email"])[0]
                        added.append(p.key)
            if "pageToken" in members:
                members = directory.members().list(groupKey=self.group_email, maxResults=1000, pageToken=members["pageToken"]).execute()
            else:
                break
        if not self.people:
            self.people = added
            self.put()
        else:
            # reset self.has_changed
            self.set_updated()
            # check if Group still exists
            try:
                directory = create_directory_service()
                exist = directory.groups().get(groupKey=self.group_email).execute()
                if not exist: return self.key.delete()
            except Exception, e:
                return self.key.delete()
            # update self.people, assuming previous sync_gapps_users() call
            removed = self.people
            intersection = list(set(added).intersection(set(removed)))
            added = list(set(added)-set(intersection))
            removed = list(set(removed)-set(intersection))
            if added or removed:
                self.has_changed = True
                for add in added:
                    self.people.append(add)
                    self.added_people.append(add)
                for rem in removed:
                    self.people.remove(rem)
                    self.removed_people.append(rem)
            self.put()