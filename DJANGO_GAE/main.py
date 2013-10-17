# -*- coding: utf-8 -*-
import os
import logging
import sys
import webapp2

from google.appengine.ext.webapp.util import run_wsgi_app

import jinja2

from authorized_decorator import authorized


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('pages'),
    variable_start_string='[[',
    variable_end_string=']]'
)

class Front(webapp2.RequestHandler):
    @authorized
    def get(self):
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render({}))

''' Application route '''
application = webapp2.WSGIApplication([('/', Front)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()