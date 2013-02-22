##############################################################################
# -*- coding: utf-8 -*-
# Project:		ControlIES
# Module:    	avahiClient.py
# Purpose:		Avahi client to detect ltsp servers
# Language:		Python 2.5
# Date:			27-Feb-2011.
# Ver:			27-Feb-2011.
# Author:		José Luis Redrejo Rodriguez
# Copyright:    2011 - José Luis Redrejo Rodriguez <jredrejo @no-spam@ debian.org>
# Modified by:  Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#
# ControlIES is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ControlIES is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ControlIES. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

try:
    import dbus
    if getattr(dbus, 'version', (0,0,0)) >= (0,41,0):
		import dbus.glib		
except ImportError:
    dbus = None

if dbus:
    try:
        import avahi
    except ImportError:
        avahi = None
else:
    avahi = None

from twisted.internet import defer, threads
from twisted.internet import glib2reactor
import logging
glib2reactor.install()

class avahiClient():

    def __init__(self, type):
		self._callbacks = {'new-service':  [], 'remove-service': [] }
		# initialize dbus stuff needed for discovery
								   
		self.bus = dbus.SystemBus()
		
		avahi_bus = self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
		self.server = dbus.Interface(avahi_bus, avahi.DBUS_INTERFACE_SERVER)
		
		#stype = '_workstation._tcp'
		#stype = '_controlaula._tcp'

		stype = type

		domain = 'local'
		self._plugged = {}

		avahi_browser = self.server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, stype, domain, dbus.UInt32(0))
		obj = self.bus.get_object(avahi.DBUS_NAME, avahi_browser)
		self.browser = dbus.Interface(obj, avahi.DBUS_INTERFACE_SERVICE_BROWSER)	

    def start(self):
		self.browser.connect_to_signal('ItemNew', self.new_service)
		self.browser.connect_to_signal('ItemRemove', self.remove_service)
		
    def stop(self):
        self.bus.close()

    def new_service(self, interface, protocol, name, type, domain, flags):
		
		def resolve_service_reply(*service):
			address, port = service[-4:-2]
			name = unicode(service[2])
			for cb in self._callbacks['new-service']:
				self._plugged[name] = (address,port)				
				cb(self,name, address, port)
				
		def resolve_service_error(exception):
			logging.getLogger().debug('could not resolve daap service %s %s: %s' % (name, domain, exception))			
			#self.warning('could not resolve daap service %s %s: %s' % (name, domain, exception))

		self.server.ResolveService(interface, protocol, name, type, domain,
				avahi.PROTO_UNSPEC, dbus.UInt32(0),
				reply_handler=resolve_service_reply,
				error_handler=resolve_service_error)

    def remove_service(self, interface, protocol, name, type, domain,server):
        address, port = self._plugged[name]
        for cb in self._callbacks['remove-service']:
            cb(self,name, address, port)


    def add_callback(self, sig_name, callback):
        self._callbacks[sig_name].append(callback)

    def remove_callback(self, sig_name, callback):
        self._callback[sig_name].remove(callback)
