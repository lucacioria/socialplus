# -*- coding: UTF-8 -*-
import httplib2
import json
import logging

from socialplus.utils import *
from socialplus.data import *
from socialplus.api import create_directory_service

from google.appengine.api import search
from google.appengine.ext import ndb

def seed_db_from_directory():
    # create circle object from directory
    #
    # connect to directory api
    # get all orgunits, subunits, groups
    # translate them into respective circles objects
    # --> then move on to seed_circles_from_db...
    
    directory = create_directory_service()
    orgunits = directory.orgunits(type="all").list  ## need example on params, need response structure
    groups = directory.groups().list
    ## model hierarchy of orgunits
    ## create Circles for orgunits, identical name or ID
    ## [later: have policy file set rules for translations process]
    
    ## get all users
    ## from user get: orgUnitPath, emails[]->primary:true
    ## store email address in respective orgUnit = Circle
    ## create the cirle object with respective email addresses

    
def seed_circles_from_db():
    # create G+ circles from circle objects
    # 
    