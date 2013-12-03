# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_plus_service, create_directory_service

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

""" HELPER FUNCTIONS """

def update_progress(sync_task, string_to_append, current_step, total_steps):
    sync_task.started = True
    sync_task.progress_message += string_to_append
    if total_steps > 0:
        sync_task.progress_percentage = int(float(current_step) * 100 / total_steps)
    else:
        sync_task.progress_percentage = 0
    sync_task.put()

def mark_as_completed(sync_task, string_to_append=""):
    sync_task.started = True
    sync_task.completed = True
    sync_task.progress_message += string_to_append
    sync_task.progress_message += "\nSUCCESS\n"
    sync_task.progress_percentage = 100
    sync_task.put()