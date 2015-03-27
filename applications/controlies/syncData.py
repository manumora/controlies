#!/usr/bin/env python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      syncData.py
# Purpose:     Synchronize with classrooms data
# Language:    Python 2.5
# Date:        27-Mar-2015.
# Ver:         27-Mar-2015.
# Author:      Manuel Mora Gordillo
# Copyright:   2015 - Manuel Mora Gordillo    <manuito @nospam@ gmail.com>
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

import threading
import time
import logging
import xmlrpclib
import ldap

class LdapConnection(object):

    def __init__(self,host):
		self.host = host

    def connect(self):		
		try:
			self.connect=ldap.open(self.host)
			self.protocol_version = ldap.VERSION3
		except ldap.LDAPError, e:
			return False
			
		return True

    def search(self,baseDN,filter,retrieveAttributes):		
		try:
			ldap_result_id = self.connect.search(baseDN+",dc=instituto,dc=extremadura,dc=es", ldap.SCOPE_SUBTREE, filter, retrieveAttributes)
			result_set = []
			while 1:
				result_type, result_data = self.connect.result(ldap_result_id, 0)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)
			return result_set
		except ldap.LDAPError, e:
			print e


# Finding LTSP Servers
l = LdapConnection("localhost")
l.connect()
search = l.search("ou=Netgroup","(cn=ltsp-server-hosts)",["nisNetgroupTriple"])

ltspServers = search[0][0][1]['nisNetgroupTriple']


rpcServer = xmlrpclib.ServerProxy("http://localhost:6969", allow_none=True)

def daemon(classroom):
    while True:
	try:
    		rpcLTSP = xmlrpclib.ServerProxy("http://"+classroom+":6800", allow_none=True)
	    	data = rpcLTSP.get_data()
		computers = data["computers"]
		pupils = data["students"]
	except:
		computers = []
		pupils = []
		pass

	try:
		rpcServer.set_data_classroom(classroom, computers, pupils)
	except:
		pass

	time.sleep(10)

for l in ltspServers:
	ltsp = l.replace("(","").replace(",-,-)","")
	threading.Thread(name='daemon', target=daemon, args=(ltsp,)).start()
	time.sleep(0.3)
