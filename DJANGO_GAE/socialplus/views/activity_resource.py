import json
import logging
import datetime as dt

from django.http import HttpResponse

from socialplus.utils import *

from socialplus.data.activities import search_activities_paginated, get_activities

def search_activities(request):
    # get query parameters
    q = request.GET.get('q', '')
    print q
    next_page_cursor = request.GET.get('nextPageCursor', None)
    page_size = request.GET.get('pageSize', 20)
    # set cursor for paginated queries
    if next_page_cursor:
        cursor = search.Cursor(web_safe_string=next_page_cursor)
        ids, next_cursor = search_activities_paginated(q, cursor, limit=page_size)
    else:
        ids, next_cursor = search_activities_paginated(q)
    # get activities from ids
    activities = [x.to_dict_for_json() for x in get_activities(ids)]
    # create json form
    return HttpResponse(format_json({
        'items': activities, 
        'nextPageCursor': next_cursor.web_safe_string if next_cursor else "null",
        'morePagesAvailable': True if next_cursor else False,
        }))