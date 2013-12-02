import logging
from google.appengine.api import users
from django.http import HttpResponse

def authorized(f):
    def decorated_call(self, *callback_args, **callback_kwargs):
    	user = users.get_current_user()
    	# check if logged in
    	if not user:
            return HttpResponse(status=401)
        else:
        	email = user.email()
    	# check if authorized
        if "@lumapps.com" in email or "@google.com" in email or "@oxylane.com" in email or "@gpartner.eu" in email:
            return f(self, *callback_args, **callback_kwargs)
        else:
            return HttpResponse(status=401)

    return decorated_call
