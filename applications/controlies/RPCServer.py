#!/usr/bin/env python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      RPCServer.py
# Purpose:     RPC Server for LDAP
# Language:    Python 2.5
# Date:        19-Nov-2013.
# Ver:         19-Nov-2013.
# Author:      Manuel Mora Gordillo
# Copyright:   2013 - Manuel Mora Gordillo    <manuito @nospam@ gmail.com>
#
# Autorename is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Autorename is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Autorename. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from SimpleXMLRPCServer import SimpleXMLRPCServer

class XMLRPCServer(SimpleXMLRPCServer):   
    def process_request(self, request, client_address):
       self.client_address = client_address[0]
       return SimpleXMLRPCServer.process_request(self, request, client_address)
       

computers = []
teachers = []
laptops = []
pupils = []

class item():
	def __init__(self, name, computer="", ip="", proxy=""):
		self.name = name
		self.computer = computer
		self.ip = ip
		self.proxy = proxy

	def getName(self):
		return self.name

	def getComputer(self):
		return self.computer

	def getIP(self):
		return self.ip

	def getProxy(self):
		return self.proxy

#************************************************************************************

def append_computer(name, ip):
	n = name.split(" ")[0]

	remove_computer(n)

	i = item(n, ip=ip)
	computers.append(i)

def remove_computer(name):
	n = name.split(" ")[0]
	for c in computers:
		if c.getName() == n:
			computers.remove(c)

def get_computers():
	tmp = []
	for c in computers:
		tmp.append(c.getName())
	return tmp

#************************************************************************************

def append_teacher(name, computer, ip):
	n = name.split(" ")[0]

	remove_teacher_from_computer(computer)

	i = item(n, computer=computer, ip=ip)
	teachers.append(i)

def remove_teacher(name, computer):
	n = name.split(" ")[0]
	for c in teachers:
		if c.getName() == n and c.getComputer() == computer:
			teachers.remove(c)

def get_teachers():
	tmp = []
	for c in teachers:
		tmp.append(c.getName()+"@"+c.getComputer())
	return tmp

def remove_teacher_from_computer(computer):
        for c in teachers:
                if c.getComputer() == computer:
                        teachers.remove(c)


#************************************************************************************

def append_laptop(name, computer, ip, proxy=""):
	n = name.split(" ")[0]

	#remove_laptop(n)

	i = item(n, ip=ip, proxy=proxy)
	laptops.append(i)

def remove_laptop(name):
	n = name.split(" ")[0]
	for c in laptops:
		if c.getName() == n:
			laptops.remove(c)

def get_laptops():
	tmp = []
	for c in laptops:
		tmp.append(c.getName())
	return tmp

def set_laptops(classroom, laptopsList):
	remove_laptops_from_classroom(classroom)

	for laptop in laptopsList:
		l = laptop.split("@")
		append_laptop(l[0],"",l[1],classroom)

def get_data_laptops(name=""):
	tmp = []
	for c in laptops:
		if name=="" or name==c.getName():
			tmp.append({"name":c.getName(), "ip": c.getIP(), "proxy": c.getProxy()})
	return tmp

def remove_laptops_from_classroom(classroom):
	for l in laptops:
		if l.getProxy() == classroom:
			laptops.remove(c)
#************************************************************************************

def append_pupil(name, computer, ip, proxy=""):
	n = name.split(" ")[0]

	remove_pupil(n)

	i = item(n, ip, proxy)
	pupils.append(i)

def remove_pupil(name):
	n = name.split(" ")[0]
	for c in pupils:
		if c.getName() == n:
			pupils.remove(c)

def set_pupils(classroom, pupils):
	for pupil in pupils:
		l = pupil.split("@")
		append_pupil(l[0],"",l[1],classroom)


def get_pupils():
	tmp = []
	for c in pupils:
		tmp.append(c.getName())
	return tmp

#************************************************************************************

server = XMLRPCServer (("", 6969), allow_none=True, logRequests = False)
#server = XMLRPCServer (("", 6969))
server.register_function (append_computer)
server.register_function (remove_computer)
server.register_function (get_computers)

server.register_function (append_teacher)
server.register_function (remove_teacher)
server.register_function (get_teachers)

server.register_function (append_laptop)
server.register_function (remove_laptop)
server.register_function (get_laptops)
server.register_function (set_laptops)
server.register_function (get_data_laptops)

server.register_function (append_pupil)
server.register_function (remove_pupil)
server.register_function (set_pupils)
server.register_function (get_pupils)

server.serve_forever()
