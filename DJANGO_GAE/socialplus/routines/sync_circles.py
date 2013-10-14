# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import * 

from google.appengine.api import search
from google.appengine.ext import ndb


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

def sync_gapps_orgunits():
    directory = create_directory_service()
    orgunits = directory.orgunits().list(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"], type="all").execute()
    for orgunit in orgunits["organizationUnits"]:
        ou = OrgUnit.new(orgunit["name"])
        users = CirclePerson.query(CirclePerson.orgUnitPath=orgunit["orgUnitPath"])
        ou.people = ndb.put_multi_async([x in users])  # is this equivalent to [x.key for x in users] ?

def sync_gapps_groups():
    directory = create_directory_service()
    groups = directory.groups().list(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"]).execute()
    for group in groups["groups"]:
        g = Group.new(name=group["name"], groupEmail=group["email"])
        members = directory.members().list(group["email"], maxResults=1000).execute()
        people = []
        while True:
            # process members
            for member in members["members"]:
                people.append(CirclePerson.find_or_create(member["email"]))
            if members["pageToken"]:
                members = directory.members().list(group["email"], maxResults=1000, pageToken=members["pageToken"]).execute()
            else:
                break
        g.people = ndb.put_multi_async([x in people])

