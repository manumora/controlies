#!/usr/bin/python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      avahiClient.py
# Purpose:     Avahi Client to detect ltsp-servers
# Language:    Python 2.5
# Date:        26-Oct-2011.
# Ver:        26-Oct-2011.
# Author:	Manuel Mora Gordillo
# Copyright:    2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
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

import dbus, gobject, avahi, os
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
import xmlrpclib

typeComputers = "_workstation._tcp"
typeTeachers = "_controlies._udp"
typeLaptops = "_laptops._tcp"
typePupils = "_pupils._tcp"

rpcServer = xmlrpclib.ServerProxy("http://localhost:6969", allow_none=True)

#####################################################################################################
def newComputer(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))

		if protocol == avahi.PROTO_INET:
			rpcServer.append_computer(str(name), str(address))
	except:
		pass

def removeComputer(interface, protocol, name, type, domain, flags):
        rpcServer.remove_computer(str(name))

#####################################################################################################
def newTeacher(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
		n = name.split(".")[0].split("@")
		if protocol == avahi.PROTO_INET:
			rpcServer.append_teacher(str(n[0]), str(n[1]), str(address))
	except:
		pass

def removeTeacher(interface, protocol, name, type, domain, flags):
	n = name.split(".")[0].split("@")
        rpcServer.remove_teacher(str(n[0]),str(n[1]))

#####################################################################################################
def newLaptop(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))

		if protocol == avahi.PROTO_INET:
			n = name.split(" ")[0]
			local_address = ''.join([chr(byte) for byte in txt[1]]).replace("address=","")
			rpcServer.append_laptop(str(n), str(n), str(local_address), str(address))
	except:
		pass

def removeLaptop(interface, protocol, name, type, domain, flags):
        rpcServer.remove_laptop(str(name))

#####################################################################################################
def newPupil(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))

		if protocol == avahi.PROTO_INET:
			local_address = ''.join([chr(byte) for byte in txt[1]]).replace("address=","")
			rpcServer.append_pupil(str(name), str(local_address), str(address))
	except:
		pass

def removePupil(interface, protocol, name, type, domain, flags):
        rpcServer.remove_pupil(str(name))

#####################################################################################################
loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=loop)
server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeComputers, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newComputer)
sbrowser.connect_to_signal("ItemRemove", removeComputer)

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeTeachers, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newTeacher)
sbrowser.connect_to_signal("ItemRemove", removeTeacher)

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeLaptops, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newLaptop)
sbrowser.connect_to_signal("ItemRemove", removeLaptop)

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typePupils, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newPupil)
sbrowser.connect_to_signal("ItemRemove", removePupil)

gobject.MainLoop().run()
