import json
import logging
import random
import time
from apiclient import errors
import datetime
import re

def dthandler(obj): 
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()    
    else:
        return None

def format_json(obj, camelize=True):
    if not obj:
        raise Exception("NoneType given to format_json")
    def to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])
    def camelize_obj(obj):
        if obj.__class__ == dict:
            for k in obj.keys():
                camelize_obj(obj[k])
                obj[to_camel_case(k)] = obj.pop(k)        
        elif obj.__class__ == list:
            for x in obj:
                camelize_obj(x)
    if camelize:
        camelize_obj(obj)
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '), default=dthandler)

# def list_of_resources_to_json(lst):
#     return "[" + ",".join([x.to_json() for x in lst]) + "]"

def query_to_obj(query_obj):
    result = []
    for entry in query_obj:
        result.append(dict([(p, unicode(getattr(entry, p))) for p in entry.properties()]))
    return result

def find_with_index(f, seq):
    """Return first item in sequence where f(item) == True."""
    for index, item in seq:
        if f(item): 
            return index, item
    return None, None

def find(f, seq):
  """Return first item in sequence where f(item) == True."""
  for item in seq:
    if f(item): 
      return item
  return None

def is_valid_utf8(str):
    if not str:
        return False
    valid_utf8 = True
    try:
        str.decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        valid_utf8 = False
    return valid_utf8

def str_to_datetime(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')

def call_with_exp_backoff(http_request):
    for n in range(0, 5):
        try:
            result = http_request.execute()
            break
        except errors.HttpError, e: #todo should do based on error type?
            error = json.loads(e.content)
            code = error["error"].get('code')
            # todo better manage different error codes
            if code < 500 and code != 403: # 403 usually is limit of unauthenticated requests (google bug?)
                print 'Error code: %d' % code
                raise e
            logging.warning("Backoff round %d (%s)" % (n, e.content))
            time.sleep((2 ** n) + random.randint(0, 1000) / 1000)
    return result
