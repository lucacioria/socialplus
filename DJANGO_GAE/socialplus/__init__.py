from google.appengine.ext import ndb

def to_dict_with_id(self):
    o = self.to_dict()
    if self.key:
        o["id"] = self.key.urlsafe()
    return o

ndb.Model.to_dict_with_id = to_dict_with_id