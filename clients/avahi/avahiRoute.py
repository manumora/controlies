#!/usr/bin/python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      avahiClientLTSP.py
# Purpose:     Avahi Client in Classroom network
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
typeStudents = "_controlies._udp"

rpcServer = xmlrpclib.ServerProxy("http://localhost:6800", allow_none=True)

def siocgifname(interface):
	if interface <= 0:
            return "n/a"
        else:
            return server.GetNetworkInterfaceNameByIndex(interface)

#####################################################################################################
def newComputer(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
		iface = siocgifname(interface)

		if protocol == avahi.PROTO_INET and address!="192.168.0.254" and (iface=="eth0" or iface=="wlan0" or iface=="br0"):
			rpcServer.append_computer(str(name), str(address))
	except:
		pass

def removeComputer(interface, protocol, name, type, domain, flags):
        rpcServer.remove_computer(str(name))

#####################################################################################################
def newStudent(interface, protocol, name, type, domain, flags):
	try:
		interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags = server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
		iface = siocgifname(interface)
		n = name.split(".")[0].split("@")

		if protocol == avahi.PROTO_INET and address!="192.168.0.254" and (iface=="eth0" or iface=="wlan0" or iface=="br0"):
			rpcServer.append_student(str(n[0]), str(n[1]), str(address))
		elif protocol == avahi.PROTO_INET and address=="192.168.0.254" and (iface=="eth0" or iface=="br0"):
			thin = ''.join([chr(byte) for byte in txt[0]]).replace("thinclient=","")
			if thin=="True":
				rpcServer.append_student(str(n[0]), str(n[1]), str(address))
	except:
		pass

def removeStudent(interface, protocol, name, type, domain, flags):
	n = name.split(".")[0].split("@")
        rpcServer.remove_student(str(n[0]),str(n[1]))

#####################################################################################################
loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=loop)
server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeComputers, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newComputer)
sbrowser.connect_to_signal("ItemRemove", removeComputer)

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeStudents, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newStudent)
sbrowser.connect_to_signal("ItemRemove", removeStudent)

gobject.MainLoop().run()
