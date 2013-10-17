# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.data.circlesources import *
from socialplus.data.circles import *
from socialplus.api import * 

from google.appengine.api import search
from google.appengine.ext import ndb


# BACKGROUND DOMAIN SYNC (run this using a scheduler, e.g. 1/day)
def sync_gapps():
    sync_gapps_users()
    sync_gapps_orgunits()
    sync_gapps_groups()

def sync_gapps_users():
    directory = create_directory_service()
    users = directory.users().list(domain=API_ACCESS_DATA[CURRENT_DOMAIN]["DOMAIN_NAME"], maxResults=500).execute()
    while True:
        for user in users["users"]:
            if "deletionTime" in user:
                CirclePerson.find_and_delete(user["primaryEmail"])
                continue
            CirclePerson.find_or_create(user["primaryEmail"], user["orgUnitPath"], user["name"]["givenName"], user["name"]["familyName"])
        if "nextPageToken" in users:
            users = directory.users().list(domain=API_ACCESS_DATA[CURRENT_DOMAIN]["DOMAIN_NAME"], maxResults=500, nextPageToken=users["nextPageToken"]).execute()
        else:
            break

def sync_gapps_orgunits():
    directory = create_directory_service()
    orgunits = directory.orgunits().list(customerId=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"], type="all").execute()
    domain_orgunits = []
    for orgunit in orgunits["organizationUnits"]:
        ou = OrgUnit.find_or_create(name=orgunit["name"], orgUnitPath=orgunit["orgUnitPath"])[0]
        domain_orgunits.append(orgunit["name"])
        ou.update_from_source()
    stored_orgunits = OrgUnits.get_list()
    print("STORED ORGUNITS")
    pprint(stored_orgunits)
    # @TODO: is there a more efficient way to subtract to lists?
    if len(domain_orgunits)!=len(stored_orgunits):
        for a in domain_orgunits:
            if a in stored_orgunits:
                domain_orgunits.remove(a)
    for name in domain_orgunits:
        find_and_delete(name)

def sync_gapps_groups():
    directory = create_directory_service()
    groups = directory.groups().list(customer=API_ACCESS_DATA[CURRENT_DOMAIN]["CUSTOMER_ID"]).execute()
    for group in groups["groups"]:
        pprint(group)
        g = Group.find_or_create(name=group["name"], group_email=group["email"])[0]
        g.update_from_source()
    # @TODO: single out and handle deleted Groups

def create_circles_test():
    inc1 = OrgUnit.query(OrgUnit.name=="Demo accounts").get().key
    inc2 = OrgUnit.query(OrgUnit.name=="Air Liquide").get().key
    wc1 = Group.query(Group.group_email=="demose@appseveryday.com").get().key
    test_circle = Circle.new(name="TestCircle", in_circle=[inc1,inc2], with_circle=[wc])
    pprint(test_circle)
    # test_circle.update()