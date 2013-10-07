import logging
import json
import datetime

from socialplus.utils import *

from google.appengine.ext import ndb

class Tag(ndb.Model):
    name            = ndb.StringProperty()
    search_strings  = ndb.StringProperty(repeated=True)

    def to_json(self):
        t = self.to_dict_with_id()
        return format_json(t)

    def to_json_light(self):
        t = self.to_dict_with_id_light()
        return format_json(t)

    def to_dict_with_id_light(self):
        t = self.to_dict_with_id()
        del t["search_strings"]
        return t