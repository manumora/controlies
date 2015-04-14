#!/usr/bin/python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      sessionControlLTSP.py
# Purpose:     Avahi Server to publish users logins
# Language:    Python 2.5
# Date:        13-Nov-2013.
# Ver:         13-Nov-2013.
# Author:	   Manuel Mora Gordillo
# Copyright:   2013 - Manuel Mora Gordillo <manuel.mora.gordillo @no-spam@ gmail.com>
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

import avahi
import dbus
import subprocess
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

__all__ = ["ZeroconfService"]

import pwd, os
loginname = ''
def getLoginName():
    global loginname
    data = pwd.getpwuid(os.getuid())
    hostname=""
    thinclient="False"
    if loginname == '':
        loginname = data[0]
        if "profesor" in data[5]:
            hostname = getHostName()
        else:
            h = subprocess.Popen(["who | grep '"+loginname+"' | awk '{ print $5}'"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]
            hostname = h.replace("(","").replace(")","").replace(".local","").rstrip()
            thinclient="True"

    return {'loginname':loginname, 'hostname':hostname, "thinclient":thinclient}

import socket
def getHostName():
    return socket.gethostname()

def isActive():
    logged = subprocess.Popen(["users"], stdout=subprocess.PIPE).communicate()[0]
    loggedusers = logged.split()
    #user = getLoginName()
    #active = user["loginname"] in loggedusers
    active = loginname in loggedusers

    return active

def checkActivity():

    def sendNext():
        if not isActive():
            reactor.stop()

    loop = LoopingCall(sendNext)
    loop.start(10)
    return

class ZeroconfService:

    def __init__(self, name, port, stype="_controlies._udp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text

    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g

    def unpublish(self):
        self.group.Reset()


if __name__ == "__main__":
    data = getLoginName()
    USERNAME = data["loginname"]
    HOSTNAME = data["hostname"]
    THINCLIENT = data["thinclient"]
    service = ZeroconfService(stype = "_controlies._udp", port = "3000", name = USERNAME + '@' + HOSTNAME, text = ["hostname=" + HOSTNAME, "thinclient=" + THINCLIENT ])
    service.publish()
    reactor.callWhenRunning(checkActivity)
    reactor.run()
