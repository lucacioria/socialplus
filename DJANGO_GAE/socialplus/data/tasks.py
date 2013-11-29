import logging
import json
import datetime

from socialplus.utils import *

from google.appengine.ext import ndb

class Task(ndb.Model):
    completed = ndb.BooleanProperty(default=False)
    started = ndb.BooleanProperty(default=False)
    creation_time = ndb.DateTimeProperty(required=True)
    name = ndb.StringProperty(required=True)
    progress_percentage = ndb.IntegerProperty(default=0)
    progress_message = ndb.TextProperty(default="waiting..")
    # custom options (depend on task)
    sync_activities_person_email = ndb.StringProperty()
    sync_activities_days = ndb.IntegerProperty()
    sync_activities_update_search_index = ndb.BooleanProperty()
    sync_people_org_unit_path = ndb.StringProperty()
    update_report_report_id = ndb.StringProperty()

    def to_json(self):
    	return format_json(self.to_dict_for_json())

    def to_dict_for_json(self):
    	t = self.to_dict_with_id()
    	return t