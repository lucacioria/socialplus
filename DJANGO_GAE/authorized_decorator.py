import logging
from google.appengine.api import users
from google.appengine.ext import webapp


def authorized(f):
    def decorated_call(self):
        if "@lumapps.com" in users.get_current_user().email() or "@google.com" in users.get_current_user().email() or "@oxylane.com" in users.get_current_user().email():
            return f(self)
        else:
            webapp.abort(401)

    return decorated_call