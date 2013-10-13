# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import * 

from google.appengine.api import search
from google.appengine.ext import ndb


# BACKGROUND DOMAIN SYNC (run this using a scheduler)
def sync_gapps():
    sync_gapps_users()
    sync_gapps_orgunits()
    sync_gapps_groups()

def sync_gapps_users():
    directory = create_directory_service()
    users = directory.users().list(domain=API_ACCESS_DATA[CURRENT_DOMAIN]["DOMAIN_NAME"], maxResults=500).execute()
    while True:
        for user in users["users"]:
            CirclePerson.find_or_create(user["primaryEmail"], user["orgUnitPath"])
        if users["nextPageToken"]:
            users = directory.users().list(domain=API_ACCESS_DATA[CURRENT_DOMAIN]["DOMAIN_NAME"], maxResults=500, nextPageToken=users["nextPageToken"]).execute()
        else:
            break
    # UPDATE: remove deleted users and add new users

def sync_gapps_orgunits():
    directory = create_directory_service()
    orgunits = directory.orgunits().list(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"], type="all").execute()
    for orgunit in orgunits["organizationUnits"]:
        ou = OrgUnit.find_or_create(name=orgunit["name"], orgUnitPath=orgunit["orgUnitPath"])
        ou.update_from_source()
            

def sync_gapps_groups():
    directory = create_directory_service()
    groups = directory.groups().list(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"]).execute()
    for group in groups["groups"]:
        g = Group.find_or_create(name=group["name"], groupEmail=group["email"])
        g.update_from_source()

def create_circles_test():
    # simple test: create circles from all orgunits and groups
    Circle.new()
    # propagate to g+ circles by calling Circle.update

