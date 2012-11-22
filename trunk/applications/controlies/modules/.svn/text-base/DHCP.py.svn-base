##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    DHCP.py
# Purpose:     DHCP class
# Language:    Python 2.5
# Date:        7-Feb-2011.
# Ver:        7-Feb-2011.
# Author:	Manuel Mora Gordillo
#			Francisco Mendez Palma
# Copyright:    2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#				2011 - Francisco Mendez Palma <fmendezpalma @no-spam@ gmail.com>
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
# along with ControlAula. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import ldap
import logging
from math import ceil

class DHCP(object):

    def __init__(self):
		pass
	
    def __init__(self,ldap,subnet_mask,broadcast_address,routers,domain_name_servers,domain_name,ntp_servers,log_servers,netbios_name_servers,netbios_node_type):
		self.ldap = ldap
		self.subnet_mask = subnet_mask
		self.broadcast_address = broadcast_address
		self.routers = routers
		self.domain_name_servers = domain_name_servers
		self.domain_name = domain_name
		self.ntp_servers = ntp_servers
		self.log_servers = log_servers
		self.netbios_name_servers = netbios_name_servers
		self.netbios_node_type = netbios_node_type
	
    def validation(self):
		if self.subnet_mask == "":
			return "subnet_mask"

		if self.broadcast_address == "broadcast_address":
			return "broadcast_address"
			
		if self.routers == "routers":
			return "routers"

		if self.domain-name == "domain-name":
			return "domain-name"
			
		if self.domain_name_servers == "domain_name_servers":
			return "domain_name_servers"
			
		if self.ntp_servers == "ntp_servers":
			return "ntp_servers"
			
		if self.log_servers == "log_servers":
			return "log_servers"

		if self.netbios_name_servers == "netbios_name_servers":
			return "netbios_name_servers"
			
		if self.netbios_node_type == "netbios_node_type":
			return "netbios_node_type"
			
		return "OK"

    def process(self,action):
		if action == "add":
			val = self.validation()
			
			if val != "OK":
				return val
			else:
				response = self.add()
				return response

		if action == "modify":
			val = self.validation()
			
			if val != "OK":
				return val
			else:
				response = self.modify()
				return response
				
		if action == "delete":
			response = self.delete()
			return response
		
		if action == "list":
			response = self.list();
			return response	
			
    def list(self,args):
		#busqueda dhcp
		search = self.ldap.search("cn=INTERNAL,cn=DHCP Config,dc=instituto,dc=extremadura,dc=es","dhcpOption=*",["dhcpOption"])

		limit = int(args['rows'][0])
		page = int(args['page'][0])

		start = limit * page - limit
		finish = start + limit;		
		
		if len(search) > 0:
			totalPages = ceil( len(search) / int(limit) )
		else:
			totalPages = 0

		if page > totalPages:
			page = totalPages
		# print search[0][0][1]["uidNumber"][0]
		rows = []
		for i in search[start:finish]:
			row = { "cn":i[0][0], "cell":[i[0][1]["cn"][0], i[0][1]["ipHostNumber"][0],i[0][1]["macAddress"]]}
			rows.append(row)

		return { "page":page, "total":totalPages, "records":len(search), "rows":rows }

    def add(self):
		record = [
		('objectclass', ['person','organizationalperson','inetorgperson']),
		('uid', ['francis']),
		('cn', [self.name] ),
		('sn', ['Bacon'] ),
		('userpassword', [self.password]),
		('ou', ['users'])
		]
		try:
			self.ldap.add("cn=hosts", record)
		except ldap.ALREADY_EXISTS:
			return "fail"
		
		return "OK"
 
    def modify(self):
		mod_attrs = [
		(ldap.MOD_ADD, 'description', 'Author of New Organon'),
		(ldap.MOD_ADD, 'description', 'British empiricist') 
		]
		self.ldap.modify_s('uid='+ uid +',cn=hosts', mod_attrs)

    def delete(self,uid):
		self.ldap.delete('uid='+ uid +',cn=hosts')

    def wakeup(self):
		from twisted.internet.task import LoopingCall
		from twisted.internet import defer
		from Plugins import NetworkUtils
		NetworkUtils.startup(self.mac)

#	def wakeup(self):
#		from twisted.internet.task import LoopingCall
#		from twisted.internet import defer
#		from Plugins import NetworkUtils
#		NetworkUtils.startup(self.mac)
		

# Encender el equipo
#def wakeup(self):
#        macs=[]
#        for i in self.targets:
#            mac=Configs.MonitorConfigs.GetMAC(i)
#            if mac !='':                
#                macs.append(mac)                
#        Actions.sendWOLBurst(macs, 2)

#Apagar el equipo
#    def sleep(self):
#        self.usersCommand(Desktop.sleep)

#def sendWOLBurst(macs,throttle):    
#    from twisted.internet.task import LoopingCall    
#    from twisted.internet import defer    
#    if not macs:
#        return defer.succeed(None)
#    d = defer.Deferred()
#    work = list(macs)
#    def sendNext():
#        if not work:
#            loop.stop()
#            d.callback(None)
#            return defer.succeed(None)
#        next = work.pop(0)
#
#        #subprocess.Popen(['wakeonlan',next ])
#        #subprocess.Popen(['wakeonlan','-i','192.168.0.255',next ])
#        NetworkUtils.startup(next)
#                   
#        return None
#    loop = LoopingCall(sendNext)
#    loop.start(throttle)
#    return d
