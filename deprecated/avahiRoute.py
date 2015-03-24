#!/usr/bin/python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      avahiRouter.py
# Purpose:     Route avahi clients between two networks
# Language:    Python 2.5
# Date:        20-Nov-2014.
# Ver:         20-Nov-2014.
# Author:      Manuel Mora Gordillo
# Copyright:   2014 - Manuel Mora Gordillo <manuel.mora.gordillo @no-spam@ gmail.com>
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

import sys, getopt, os
import avahi, gobject, dbus
import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop
import socket

urlproto = { "_controlies._udp" : "controlies", "_workstation._tcp" : "workstation" }
use_host_names = None
domain = "local"

__all__ = ["ZeroconfService"]

class ZeroconfService:

    def __init__(self, name, port, stype="_controlies._udp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = int(port)
        self.text = text

    def publish(self):
        self.bus = dbus.SystemBus()
        self.server = dbus.Interface(
                         self.bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    self.bus.get_object(avahi.DBUS_NAME,
                                   self.server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g

    def unpublish(self):
        self.group.Reset()

    def getName(self):
	return self.name


class AvahiBookmarks:
    services = {}
    zeroConf_laptops = []
    zeroConf_pupils = []

    def __init__(self, use_host_names):

	loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), avahi.DBUS_INTERFACE_SERVER)

        self.version_string = self.server.GetVersionString()

        self.browse_service_type("_controlies._udp")
        self.browse_service_type("_workstation._tcp")

        if use_host_names is None:
            try: 
                self.use_host_names = self.server.IsNSSSupportAvailable()
            except:
                self.use_host_names = False
        else:
            self.use_host_names = use_host_names

    def browse_service_type(self, stype):

        global domain

        browser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, stype, domain, dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)

	if stype=="_controlies._udp":
        	browser.connect_to_signal('ItemNew', self.new_pupil)
        	browser.connect_to_signal('ItemRemove', self.remove_pupil)
	else:
                browser.connect_to_signal('ItemNew', self.new_computer)
                browser.connect_to_signal('ItemRemove', self.remove_computer)

    def protoname(self,protocol):
        if protocol == avahi.PROTO_INET:
            return "IPv4"
        if protocol == avahi.PROTO_INET6:
            return "IPv6"
        return "n/a"

    def siocgifname(self, interface):
        if interface <= 0:
            return "n/a"
        else:
            return self.server.GetNetworkInterfaceNameByIndex(interface)

    def get_interface_name(self, interface, protocol):
        if interface == avahi.IF_UNSPEC and protocol == avahi.PROTO_UNSPEC:
            return "Wide Area"
        else:
            return str(self.siocgifname(interface)) + " " + str(self.protoname(protocol))

    def new_computer(self, interface, protocol, name, type, domain, flags):
	try:
	        interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = self.server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
		iface = self.siocgifname(interface)

		if self.protoname(protocol)=="IPv4" and address!="192.168.0.254" and (iface=="eth0" or iface=="wlan0"):
			hostname = socket.gethostname()
			#self.imprime("New computer: "+str(name))
		    	service = ZeroconfService(stype = "_laptops._tcp", port = 3000, name = str(name), text= ["address="+str(address), "hostname="+str(hostname)])
		    	service.publish()

			self.zeroConf_laptops.append(service)
	        #self.services[(interface, protocol, name, type, domain)] = (host, aprotocol, h, port, txt)
	except:
		pass

    def remove_computer(self, interface, protocol, name, type, domain, flags):
        try:
		iface = self.siocgifname(interface)

		if self.protoname(protocol)=="IPv4" and (iface=="eth0" or iface=="wlan0"):
			#self.imprime("Remove computer: "+str(name))
			for z in self.zeroConf_laptops:
				if z.getName() == name:
					z.unpublish()
					self.zeroConf_laptops.remove(z)
		
	        #del self.services[(interface, protocol, name, type, domain)]
        except:
                pass

    def new_pupil(self, interface, protocol, name, type, domain, flags):
	try:
	        interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = self.server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
		iface = self.siocgifname(interface)

		if self.protoname(protocol)=="IPv4" and address!="192.168.0.254" and (iface=="eth0" or iface=="wlan0"):
			hostname = socket.gethostname()
			#self.imprime("New pupil: "+str(name))
		    	service = ZeroconfService(stype = "_pupils._tcp", port = 3000, name = str(name), text= ["address="+str(address), "hostname="+str(hostname)])
		    	service.publish()

			self.zeroConf_pupils.append(service)
	        #self.services[(interface, protocol, name, type, domain)] = (host, aprotocol, h, port, txt)
	except:
		pass

    def remove_pupil(self, interface, protocol, name, type, domain, flags):
        try:
		iface = self.siocgifname(interface)

		if self.protoname(protocol)=="IPv4" and (iface=="eth0" or iface=="wlan0"):
			#self.imprime("Remove pupil: "+str(name))
			for z in self.zeroConf_pupils:
				if z.getName() == name:
					z.unpublish()
					self.zeroConf_pupils.remove(z)

	        #del self.services[(interface, protocol, name, type, domain)]
        except:
                pass


    def imprime(self,imprimir):
	print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
	print imprimir
	print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

if __name__ == "__main__":
	AvahiBookmarks(use_host_names)
	gobject.MainLoop().run()
