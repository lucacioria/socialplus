import logging
from google.appengine.api import users
from google.appengine.ext import webapp


def authorized(f):
    def decorated_call(self, *callback_args, **callback_kwargs):
        if "@lumapps.com" in users.get_current_user().email() or "@google.com" in users.get_current_user().email() or "@oxylane.com" in users.get_current_user().email() or "@gpartner.eu" in users.get_current_user().email():
            return f(self, *callback_args, **callback_kwargs)
        else:
            webapp.abort(401)

    return decorated_call