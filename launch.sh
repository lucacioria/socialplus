#!/bin/sh
python $APPENGINE/dev_appserver.py --datastore_path="./datastore" --search_indexes_path="./.search_index" --port 8888 DJANGO_GAE