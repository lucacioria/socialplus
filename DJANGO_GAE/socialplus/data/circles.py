import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search
from socialplus.utils import *

class Circle(ndb.Model):
    name                = ndb.StringProperty()
    emails_in_circle    = ndb.StringProperty()
    emails_with_circle  = ndb.StringProperty()

    def to_json(self):
    	o = self.to_dict_with_id()
    	return format_json(o)