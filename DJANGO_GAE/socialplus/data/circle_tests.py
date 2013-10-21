# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import * 

from google.appengine.api import search
from google.appengine.ext import ndb

