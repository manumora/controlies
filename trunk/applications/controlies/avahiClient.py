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
import tempfile
#import memcache

typeComputers = "_workstation._tcp"
typeTeachers = "_controlaula._udp"

"""fs = tempfile.NamedTemporaryFile(delete=False, prefix='controlies_')
ft = tempfile.NamedTemporaryFile(delete=False, prefix='controlies_')
fileNameServers = fs.name
fileNameTeachers = ft.name"""

directory = "/tmp/"
fileNameServers = directory+"controliesSerFDidisDSs43"
fileNameTeachers = directory+"controliesTeaRssdASWe234"


if os.path.isfile(fileNameServers):
	os.remove(fileNameServers)

if os.path.isfile(fileNameTeachers):
	os.remove(fileNameTeachers)

f = open(fileNameServers, 'w')
f = open(fileNameTeachers, 'w')

os.chmod(fileNameServers,0755)
os.chmod(fileNameTeachers,0755)

def newComputer(interface, protocol, name, stype, domain, flags):
	computerToAdd = name.split(" ")
	
	f = open(fileNameServers, 'a')
	f.write(computerToAdd[0]+" ")
	f.close()

def removeComputer(interface, protocol, name, stype, domain, flags):
	computerToDelete = name.split(" ")
	f = open(fileNameServers, 'r')
	computersList = f.read()
	f.close()

	computersList = computersList.replace(computerToDelete[0]+" ","")

	f = open(fileNameServers, 'w')      
	f.write(computersList)
	f.close()	

def newTeacher(interface, protocol, name, stype, domain, flags):
	computerToAdd = name.split(" ")
	
	f = open(fileNameTeachers, 'a')
	f.write(computerToAdd[0]+" ")
	f.close()

def removeTeacher(interface, protocol, name, stype, domain, flags):
	computerToDelete = name.split(" ")
	f = open(fileNameTeachers, 'r')
	computersList = f.read()
	f.close()

	computersList = computersList.replace(computerToDelete[0]+" ","")

	f = open(fileNameTeachers, 'w')        
	f.write(computersList)
	f.close()


"""shared = memcache.Client(['127.0.0.1:11211'], debug=0)
shared.set('fileNameServers', fileNameServers)
shared.set('fileNameTeachers', fileNameTeachers)"""

loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=loop)
server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeComputers, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newComputer)
sbrowser.connect_to_signal("ItemRemove", removeComputer)

sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME, server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, typeTeachers, 'local', dbus.UInt32(0))), avahi.DBUS_INTERFACE_SERVICE_BROWSER)
sbrowser.connect_to_signal("ItemNew", newTeacher)
sbrowser.connect_to_signal("ItemRemove", removeTeacher)

gobject.MainLoop().run()
