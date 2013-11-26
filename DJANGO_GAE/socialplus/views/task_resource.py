import json
import logging
import datetime

from django.http import HttpResponse

from socialplus.utils import *
from socialplus.data.tasks import Task
from socialplus.routines import sync_users, sync_people, \
  sync_activities, update_search_index, update_report

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

def get_task(request, id_):
    task = ndb.Key(urlsafe=id_).get()
    return HttpResponse(task.to_json())

def get_tasks(request):
    q = Task.query(ancestor=ndb.Key("Domain", "main")).order(-Task.creation_time).fetch(999)
    tasks = [x.to_dict_for_json() for x in q]
    return HttpResponse(format_json({"items": tasks}))

def get_tasks_completed(request):
    q = Task.query(Task.completed==True, ancestor=ndb.Key("Domain", "main")).fetch(999)
    tasks = [x.to_dict_for_json() for x in q]
    return HttpResponse(format_json({"items": tasks}))

def get_tasks_active(request):
    q = Task.query(Task.completed==False, ancestor=ndb.Key("Domain", "main")).fetch(999)
    tasks = [x.to_dict_for_json() for x in q]
    return HttpResponse(format_json({"items": tasks}))

def create_task(request):
    # get post parameters
    data = json.loads(request.body)
    options = {}
    if "options" in data:
        options = data["options"]
    # create and put Task
    task = Task(parent=ndb.Key("Domain", "main"))
    task.name = data["name"]
    # custom task options
    task.sync_activities_person_email = options.get("personEmail")
    task.update_report_report_id = options.get("reportId")
    task.sync_people_org_unit_path = options.get("orgUnitPath")
    #
    task.creation_time = datetime.datetime.now()
    id_ = task.put().urlsafe()
    # call routine url with id of Task object
    taskqueue.add(url="/start_task/" + id_, method="GET", queue_name="sync-linear", target='sync')
    # return task and 201
    return HttpResponse(task.to_json(), status=201)

def create_task_cron_shortcut(request, name):
    # create and put Task
    task = Task(parent=ndb.Key("Domain", "main"))
    task.name = name
    task.creation_time = datetime.datetime.now()
    id_ = task.put().urlsafe()
    # call routine url with id of Task object
    taskqueue.add(url="/start_task/" + id_, method="GET", queue_name="sync-linear", target='sync')
    # return task and 201
    return HttpResponse(task.to_json(), status=201)

def get_post_tasks(request):
    if request.method == 'GET':
        return get_tasks(request)
    elif request.method == 'POST':
        return create_task(request)

def delete_tasks_completed(request):
    ndb.delete_multi(Task.query(Task.completed==True).fetch(9999, keys_only=True))
    return HttpResponse(status=204)

def get_delete_tasks_completed(request):
    if request.method == 'GET':
        return get_tasks_completed(request)
    elif request.method == "DELETE":
        return delete_tasks_completed(request)

def start_task(request, id_):
    # retrieve Task object from datastore
    key = ndb.Key(urlsafe=id_)
    task = key.get()
    if task.name == "syncUsers":
        sync_users(task)
    elif task.name == "syncPeople":
        sync_people(task)
    elif task.name == "syncActivities":
        sync_activities(task)
    elif task.name == "updateSearchIndex": 
        update_search_index(task)
    elif task.name == "updateReport": 
        update_report(task)
    # elif task.name == "updateTags":
    #     sync_expert_areas(task)
    else:
        return HttpResponse("TASK DOES NOT EXIST!")
    # return a HTTP 200
    return HttpResponse()

def get_task_progress(request, taskId):
    # retrieve SyncTask object from datastore
    key = ndb.Key(urlsafe=taskId)
    sync_task = key.get()

    # create progress json
    progress = {
        "name" : sync_task.name,
        "started" : sync_task.started,
        "completed" : sync_task.completed,
        "progress_message" : sync_task.progress_message,
        "progress_percentage" : sync_task.progress_percentage,
    }

def get_all_running_tasks(request):
    q = SyncTask.query().order(-SyncTask.creation_time).fetch(100)
    o = []
    for item in q:
        t = {}
        t["name"] = item.name
        t["creation_time"] = item.creation_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        t["progress_percentage"] = item.progress_percentage
        t["progress_message"] = item.progress_message
        t["started"] = item.started
        t["completed"] = item.completed
        o.append(t)
    return HttpResponse(format_json(o))

def delete_completed_tasks(request):
    q = SyncTask.query().fetch(100)
    o = [i.key for i in q]
    ndb.delete_multi(o)
        
    return HttpResponse(str(len(o)) + " tasks deleted")


# def start_sync(request, taskName):
#     # generate unique task id as micros from epoch 
#     now = dt.datetime.now()
#     # additional arguments
#     # data = json.loads(request.body)
#     # create SyncTask object and put in datastore
#     sync_task = SyncTask()
#     # sync_task.id_ = id_
#     sync_task.name = taskName
#     sync_task.creation_time = now
#     id_ = sync_task.put().urlsafe()
#     # call sync url with id of SyncTask object
#     taskqueue.add(url="/sync/" + id_, method="GET", queue_name="sync-linear")#, payload=format_json(data))
    
#     # return url to get task progress
#     task_progress_url = "/task/progress/" + id_
#     return HttpResponse(task_progress_url)