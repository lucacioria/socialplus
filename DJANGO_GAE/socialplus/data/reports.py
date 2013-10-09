import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search

from socialplus.utils import *
from socialplus.data.people import Person
from socialplus.data.activities import Activity

class RestrictedCount(ndb.Model):
    restricted = ndb.IntegerProperty(default=0)
    non_restricted = ndb.IntegerProperty(default=0)

class VisibilityCount(ndb.Model):
    shared_privately = ndb.IntegerProperty(default=0)
    extended_circles = ndb.IntegerProperty(default=0)
    public = ndb.IntegerProperty(default=0)
    domain = ndb.IntegerProperty(default=0)
    private_community = ndb.IntegerProperty(default=0)
    public_community = ndb.IntegerProperty(default=0)
    restricted_community = ndb.IntegerProperty(default=0)

    def increase_count_for_visibility(self, visibility):
        if visibility == "shared privately":
            self.shared_privately += 1
        elif visibility == "extended circles":
            self.extended_circles += 1
        elif visibility == "public":
            self.public += 1
        elif visibility == "domain":
            self.domain += 1
        elif visibility == "private community":
            self.private_community+= 1
        elif visibility == "public community":
            self.public_community += 1
        elif visibility == "restricted community":
            self.restricted_community += 1

class ActivePerson(ndb.Model):
    person = ndb.KeyProperty(kind=Person)
    total = ndb.IntegerProperty(default=0)

class PopularActivity(ndb.Model):
    activity = ndb.KeyProperty(kind=Activity)
    plus_ones = ndb.IntegerProperty(default=0)
    reshares = ndb.IntegerProperty(default=0)

class ReportData(ndb.Model):
    # time interval, meaning depends on container. ignored if in data_ever
    interval = ndb.DateProperty()
    # actual data
    restricted_count = ndb.LocalStructuredProperty(RestrictedCount)
    visibility_count = ndb.LocalStructuredProperty(VisibilityCount)
    active_people = ndb.LocalStructuredProperty(ActivePerson, repeated=True)
    popular_activities = ndb.LocalStructuredProperty(PopularActivity, repeated=True)
    total_number_of_activities = ndb.IntegerProperty(default=0)

    def __init__(self):
        # initialize new ReportData entity with nested entities
        super(ReportData, self).__init__()
        self.restricted_count = RestrictedCount()
        self.visibility_count = VisibilityCount()

    def update_with_activity(self, a):
        rd = self
        # update total count
        rd.total_number_of_activities += 1
        # update restricted count
        if a.access.domain_restricted:
            rd.restricted_count.restricted += 1
        else:
            rd.restricted_count.non_restricted += 1
        # update visibility count
        rd.visibility_count.increase_count_for_visibility(a.access.visibility)
        # update most active user
        current_person_key = a.actor
        active_person_for_current = None
        for active_person in rd.active_people:
            if active_person.person == current_person_key:
                active_person_for_current = active_person
        if active_person_for_current == None:
            active_person_for_current = ActivePerson()
            active_person_for_current.person = current_person_key
            rd.active_people.append(active_person_for_current)
        active_person_for_current.total += 1
        # update list of popular activities based on +1
        # if >= 3 pop activities and last has less +1, remove last
        if len(rd.popular_activities) >= 3 and \
           rd.popular_activities[-1].plus_ones < a.object_.plusones:
            del rd.popular_activities[-1]
        # if < 3 pop activities, insert it at right position
        if len(rd.popular_activities) < 3:
            new_pop = PopularActivity()
            new_pop.activity = a.key
            new_pop.plus_ones = a.object_.plusones
            new_pop.reshares = a.object_.reshares
            # insert and sort
            rd.popular_activities.append(new_pop)
            rd.popular_activities.sort(key = lambda x: -x.plus_ones)
        # return self for chaining
        return self

# custom reports based on search
class Report(ndb.Model):
    name = ndb.StringProperty(required=True)
    last_updated = ndb.DateTimeProperty()
    search_string = ndb.TextProperty(default="")
    # report data by time
    data_ever = ndb.LocalStructuredProperty(ReportData)
    data_by_day = ndb.LocalStructuredProperty(ReportData, repeated=True)
    data_by_month = ndb.LocalStructuredProperty(ReportData, repeated=True)
    data_by_year = ndb.LocalStructuredProperty(ReportData, repeated=True)

    def to_dict_for_json(self):
        o = self.to_dict_with_id()
        # replace keys to active people with actual person entities
        def get_nested(rd):
            for active_person in rd['active_people']:
                active_person['person'] = active_person['person'].get().to_dict_for_json()
            for popular_activity in rd['popular_activities']:
                popular_activity['activity'] = popular_activity['activity'].get().to_dict_for_json()
        map(lambda x: map(get_nested, x), [o['data_by_day'], o['data_by_month'], o['data_by_year'], [o['data_ever']]])
        return o

    def to_dict_for_json_light(self):
        o = self.to_dict_with_id()
        del o["data_ever"]
        del o["data_by_day"]
        del o["data_by_month"]
        del o["data_by_year"]
        return o

    def to_json(self):
        return format_json(self.to_dict_for_json())
    
    def to_json_light(self):
        return format_json(self.to_dict_for_json_light())

    def update_with_activity(self, a):
        r = self
        # update data_ever
        r.data_ever.update_with_activity(a)
        # update data_by_day
        # create date object for activity
        activity_day = a.published.date()
        # check if day exists, otherwise create it
        report_data_day = None
        for existing_report_data in r.data_by_day:
            if existing_report_data.interval == activity_day:
                report_data_day = existing_report_data
        if report_data_day == None:
            report_data_day = ReportData()
            report_data_day.interval = activity_day
            r.data_by_day.append(report_data_day)
        # update data_by_month
        # create date object for activity
        activity_month = a.published.date().replace(day=1)
        # check if month exists, otherwise create it
        report_data_month = None
        for existing_report_data in r.data_by_month:
            if existing_report_data.interval == activity_month:
                report_data_month = existing_report_data
        if report_data_month == None:
            report_data_month = ReportData()
            report_data_month.interval = activity_month
            r.data_by_month.append(report_data_month)
        # update data_by_year
        # create date object for activity
        activity_year = a.published.date().replace(day=1, month=1)
        # check if year exists, otherwise create it
        report_data_year = None
        for existing_report_data in r.data_by_year:
            if existing_report_data.interval == activity_year:
                report_data_year = existing_report_data
        if report_data_year == None:
            report_data_year = ReportData()
            report_data_year.interval = activity_year
            r.data_by_year.append(report_data_year)        
        # update report data with activity
        report_data_day.update_with_activity(a)
        report_data_month.update_with_activity(a)
        report_data_year.update_with_activity(a)
        # return self for chaining
        return self

    def reset_data(self):
        self.data_ever = ReportData()
        self.data_by_day = []
        self.data_by_month = []
        self.data_by_year = []
        # return self for chaining
        return self