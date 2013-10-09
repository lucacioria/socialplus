import logging
import json
import datetime

from google.appengine.ext import ndb
from google.appengine.api import search
from socialplus.utils import *

class Circle(ndb.Model):
    name                    = ndb.StringProperty()
    emails_in_circle        = ndb.StringProperty()
    emails_with_circle      = ndb.StringProperty()
    last_domain_update   = ndb.DateTimeProperty()
    last_gplus_update       = ndb.DateTimeProperty()
    
    def needs_domain_update(self):
        # ...
    
    def needs_gplus_update(self):
        # ...
        
    def sync_with_domain(self):
        # ...
    
    def sync_with_gplus(self):
        # ...


    def to_json(self):
    	o = self.to_dict_with_id()
    	return format_json(o)