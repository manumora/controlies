#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Fred Gansevles <fred@gansevles.net>
# 
# subwsgihandler.py -- a *hack* to make web2py sub-url mountable
#
# example apache config
#
#        WSGIScriptAlias /web2py /usr/local/www/wsgi-scripts/web2py/subwsgihandler.py
#        WSGIDaemonProcess subweb2py user=www-data group=www-data \
#                          home=/usr/local/www/wsgi-scripts processes=5 \
#                          maximum-requests=10000
#
#        <Location "/web2py">
#            Order deny,allow
#            Allow from all
#            WSGIProcessGroup subweb2py
#        </Location>
#
# the web2p app is now mounted at http://localhost/web2py
#

import sys
sys.path.insert(0, '')

class SubWeb2py(object):
    def __init__(self, application):
        self.application = application

        import gluon.html
        self.gluon_html_URL = gluon.html.URL
        gluon.html.URL = self.URL

    def URL(self, *args, **kw):
        # rewrite the generated URLs, so external referencens have the SCRIPT_NAME prefix
        return self.script_name + self.gluon_html_URL(*args, **kw)

    def start_response(self, status, headers, info=None):
        # rewrite redirect URLs, so external referencens have the SCRIPT_NAME prefix
        if not status.startswith('3'):
            return self._start_response(status, headers, info)
        # status: 3xx (redirect)
        _headers = []
        for key, value in headers:
            #if key == 'Set-Cookie':
                # don't modify the cookie, it already has a modified location
                #return self._start_response(status, headers, info)
            # relative URLs start with '/', absolute URLs start with 'http'
            if key == 'Location' and value.startswith('/'):
                value = self.script_name + value
            _headers.append((key, value))
        return self._start_response(status, _headers, info)

    def __call__(self, environ, start_response):
        self.script_name = environ['SCRIPT_NAME']
        environ['SCRIPT_NAME'] = ''
        if self.script_name and environ['REQUEST_URI'].startswith(self.script_name):
            environ['REQUEST_URI'] = environ['REQUEST_URI'][len(self.script_name):]
        self._start_response = start_response
        return self.application(environ, self.start_response)

from web2py.wsgihandler import application
application = SubWeb2py(application)
