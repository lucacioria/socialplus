import logging
import json
from google.appengine.ext import ndb

class Domain(ndb.Model):
    user_count       = ndb.IntegerProperty(default=0)
    person_count     = ndb.IntegerProperty(default=0)
    activities_count = ndb.IntegerProperty(default=0)