##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    Thinclients.py
# Purpose:     Thinclients class
# Language:    Python 2.5
# Date:        4-Oct-2011.
# Ver:        4-Oct-2011.
# Author:   Manuel Mora Gordillo
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

import ldap
import logging
import time
from math import floor
from operator import itemgetter
from Utils import ValidationUtils
from applications.controlies.modules.Users import Users

class Thinclients(object):

    def __init__(self):
        pass
    
    def __init__(self,ldap,name,mac,serial,username,ip=""):
        self.ldap = ldap
        self.name = name
        self.mac = mac
        self.serial = serial
        self.username = username
        self.ip = ip

    def validation(self,action):
        
        if self.name == "":
            return "name"

        if action == "add":
            if self.existsHostname():
                return "hostAlreadyExists"

        if self.mac == "":
            return "mac"

        if not ValidationUtils.validMAC(self.mac):
            return "mac"                        
        
        if action == "add":                            
            if self.existsMAC():
                return "macAlreadyExists"

        elif action == "modify":
            if not self.equalMAC():
				if self.existsMAC():
					return "macAlreadyExists"

        if self.username != "":
            u = Users(self.ldap,"","","","",self.username,"","","","")
            exists = u.existsUsername()
            if not exists:
                return "userNotExists"            

        return "OK"

    def process(self,action):

        if action == "add":
            val = self.validation(action)
            
            if val != "OK":
                return val
            else:
                response = self.add()
                return response

        if action == "modify":
            val = self.validation(action)
            
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
                
        # grid parameters
        limit = int(args['rows'])
        page = int(args['page'])
        start = limit * page - limit
        finish = start + limit;             

        # sort by field
        sortBy = args['sidx']
        #if sortBy == "uid":
            #sortBy = "id"

        # reverse Sort
        reverseSort = False
        if args['sord'] == "asc":
            reverseSort = True
        
        search = self.ldap.search("cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn","dhcpHWAddress","uniqueIdentifier","dhcpComments","dhcpStatements"])
        filter="(|(dhcpOption=*subnet*)(dhcpOption=*log*))"
        rows = []

        try:
            host_search = args["cn"] or ""
        except:
            host_search = ""
            
        try:
            mac_search = args["mac"] or ""
        except:
            mac_search = ""

        try:
            user_search = args["username"] or ""
        except:
            user_search = ""

        try:
            serial_search = args["serial"] or ""
        except:
            serial_search = ""

        try:
            ip_search = args["ip"] or ""
        except:
            ip_search = ""

        # esto hay que cambiarlo: tenemos 4 groups en thinclientes
        for i in search[6:len(search)]:
            if len(i[0][0].split(","))>6:
            
                host = i[0][1]["cn"][0]
                try:
                    mac = i[0][1]["dhcpHWAddress"][0].replace("ethernet","").strip()
                except:
                    mac = ""

                try:
                    username = i[0][1]["uniqueIdentifier"][0].replace("user-name","").strip()
                except:
                    username = ""

                try:
                    serial = i[0][1]["dhcpComments"][0].replace("serial-number","").strip()
                except:
                    serial = ""

                try:
                    matching = [s for s in i[0][1]["dhcpStatements"] if "fixed-address" in s]
                    ip=""
                    if matching:
                    	ip=matching[0].replace("fixed-address ","")
                except:
                    ip = ""

                if ((host_search != "" and host.find(host_search)>=0) or (host_search=="")) and ((mac_search != "" and mac.find(mac_search)>=0) or (mac_search=="")) and ((ip_search != "" and ip.find(ip_search)>=0) or (ip_search=="")) and ((serial_search != "" and serial.find(serial_search)>=0) or (serial_search=="")) and ((user_search != "" and username.find(user_search)>=0) or (user_search=="")):# and ((ip_search != "" and ip.find(ip_search)>=0) or (ip_search=="")):
    				nodeinfo=i[0][0].replace ("cn=","").split(",")
    				row = {
    					"id":host, 
    					"cell":[host, mac,ip , username, serial],
    					"cn":host,
    					"dhcpHWAddress":mac,
    					"ip":ip,
    					"uniqueIdentifier":username,
    					"serial":serial,
    				}             
    				rows.append(row)

        if len(rows) > 0:
            totalPages = floor( len(rows) / int(limit) )
            module = len(rows) % int(limit)

            if module > 0:
				totalPages = totalPages+1
        else:
            totalPages = 0
            
        if page > totalPages:
            page = totalPages
			
        result = sorted(rows, key=itemgetter(sortBy), reverse=reverseSort)
        return { "page":page, "total":totalPages, "records":len(rows), "rows":result[start:finish] }                    
          

    def add(self):
        classroom = self.getClassroom()
        groups = self.getThinclientGroups()
        
        if not classroom in groups['groups']:
            self.newGroup(classroom)

        if self.getTypeComputer()=="o":
            attr = [
            ('objectclass', ['top','dhcpHost']),
            ('cn', [self.name] ),
            ('dhcpStatements', ['filename "/var/lib/tftpboot/ltsp/i386/pxelinux.0"','fixed-address ' + self.ip] ), 
            ('dhcpHWAddress', ['ethernet ' + self.mac] )
            ]		
        else:
            attr = [
            ('objectclass', ['top','dhcpHost','lisPerson']),
            ('cn', [self.name] ),
            ('dhcpStatements', ['fixed-address ' + self.ip] ), 
            ('dhcpComments', ['serial-number ' + self.serial] ), 
            ('dhcpHWAddress', ['ethernet ' + self.mac] ),
            ('uniqueIdentifier', ['user-name ' + self.username]),
            ]
                        
        self.ldap.add("cn="+self.name +",cn="+classroom+",cn=THINCLIENTS,cn=DHCP Config", attr)
            
        return "OK"
        
    def modify(self):
        if self.getTypeComputer()=="o":
            attr = [(ldap.MOD_REPLACE, 'dhcpHWAddress', ['ethernet ' + self.mac]),
            (ldap.MOD_REPLACE, 'dhcpStatements', ['filename "/var/lib/tftpboot/ltsp/i386/pxelinux.0"', 'fixed-address ' + self.ip])
            ]
        else:
            attr = [
            (ldap.MOD_REPLACE, 'dhcpHWAddress', ['ethernet ' + self.mac] ),
            (ldap.MOD_REPLACE, 'dhcpComments', ['serial-number ' + self.serial] ),      
            (ldap.MOD_REPLACE, 'uniqueIdentifier', ['user-name ' + self.username] ),
            (ldap.MOD_REPLACE, 'dhcpStatements', ['fixed-address ' + self.ip])
            ]
            
        self.ldap.modify("cn="+self.name+",cn="+self.getGroup()+",cn=THINCLIENTS,cn=DHCP Config", attr)            
        return "OK"

    def modifyUser(self):
        attr = [(ldap.MOD_REPLACE, 'uniqueIdentifier', ['user-name ' + self.username])]
        self.ldap.modify("cn="+self.name+",cn="+self.getGroup()+",cn=THINCLIENTS,cn=DHCP Config", attr)
        return "OK"

    def modifyIP(self):
        if self.getTypeComputer()=="o":
            attr = [(ldap.MOD_REPLACE, 'dhcpStatements', ['filename "/var/lib/tftpboot/ltsp/i386/pxelinux.0"', 'fixed-address ' + self.ip])]
        else:
            attr = [(ldap.MOD_REPLACE, 'dhcpStatements', ['fixed-address ' + self.ip])]

        self.ldap.modify("cn="+self.name+",cn="+self.getGroup()+",cn=THINCLIENTS,cn=DHCP Config", attr)
        return "OK"

    def delete(self):
        group = self.getGroup()
        if group != "noGroup":
            self.ldap.delete('cn='+ self.name +',cn='+group+',cn=THINCLIENTS,cn=DHCP Config')

        return "OK"     


    def move(self,purpose):
        data = self.getHostData()
        self.delete()

        self.name= purpose
        self.mac= data['mac']
        self.serial= data['serial']
        self.username= data['username']	
        self.add()

        return "OK"
               
            
    def existsHostname(self):
        result = self.ldap.search("cn=THINCLIENTS,cn=DHCP Config","cn="+self.name,["cn"])
        
        if len(result) > 0:
            return True
        
        return False
        
    def existsMAC(self):     
        result = self.ldap.search("cn=THINCLIENTS,cn=DHCP Config","dhcpHWAddress=*",["dhcpHWAddress"])
        #for i in range (0, len(result) - 1):
        for i in range (0, len(result)):
            if result [i][0][1]['dhcpHWAddress'][0].replace ("ethernet", "").strip() == self.mac:
				return True
        
        return False

    def equalMAC(self):
        result = self.ldap.search("cn=THINCLIENTS,cn=DHCP Config","cn="+self.name,["dhcpHWAddress"])
        if result[0][0][1]['dhcpHWAddress'][0].replace("ethernet", "").strip() == self.mac:
            return True
        
        return False

       
    def getName (self):
        return self.mac   

    def getHostData(self):
        g = self.getGroup()
        result = self.ldap.search("cn="+g+",cn=THINCLIENTS,cn=DHCP Config","cn="+self.name,["cn","dhcpHWAddress","dhcpComments","uniqueIdentifier","dhcpStatements"])

        serial=""
        username=""
        if self.getTypeComputer()=="p":
            try:              
                serial = result[0][0][1]["dhcpComments"][0].replace("serial-number","").strip()
            except:
                serial = ""
                
            try:
                username = result[0][0][1]["uniqueIdentifier"][0].replace("user-name","").strip()
            except:
                username = ""

        try:
            matching = [s for s in result[0][0][1]["dhcpStatements"] if "fixed-address" in s]
            ip=""
            if matching:
                ip=matching[0].replace("fixed-address ","")
        except:
            ip = ""

        dataHost = {
            "cn":self.name,
            "mac":result[0][0][1]["dhcpHWAddress"][0].replace("ethernet","").strip(),
            "ip":ip,
            "serial":serial,
            "username":username
        }
        return dataHost    

    def getGroup (self):
        groups = self.getThinclientGroups()   
        for g in groups['groups']:
            search = self.ldap.search("cn="+g+",cn=THINCLIENTS,cn=DHCP Config","cn="+self.name,["cn"])
            if len(search) == 1:
                return g
            
        return "noGroup"


    def getThinclientGroups (self):
        groups = []
        search = self.ldap.searchOneLevel("cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn"])
        for g in search:
            if g[0][1]["cn"][0]!="192.168.0.0":
                groups.append (g[0][1]["cn"][0])

        return { "groups":groups }


    def groupOverflow(self,group,overflow):
        search = self.ldap.search("cn="+group+",cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn"])       
        if len(search)-2 >= overflow:
            return True
                
        return False
    

    def getFreeGroup (self):
        freeGroup = []
        groups = self.getThinclientGroups()        
        for g in groups['groups']:
            if not self.groupOverflow(g,300):
                return { "freeGroup":g }

        return { "freeGroup" : 'noFreeGroup' }
    
    def newGroup(self,nameGroup):
        attr = [
        ('objectclass', ['top','dhcpGroup','dhcpOptions']),
        ('cn', [nameGroup] ),
        ('dhcpStatements', ['next-server 192.168.0.254','use-host-decl-names on'] ),
        ('dhcpoption', ['log-servers ltspserver'] ),
        ]
                        
        self.ldap.add("cn="+nameGroup+",cn=THINCLIENTS,cn=DHCP Config", attr)
        
        return True

    def getClassroom(self):
        classroom = self.name.split("-")
        return classroom[0]
    
    def getTypeComputer(self):
        try:
            c = self.name.split("-")
            cadena = c[1][:1]
        except:
            cadena = ""
             
        return cadena
    
    def getAllComputersNode(self,node):
        computers = []
        search = self.ldap.searchOneLevel("cn="+node+",cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn"])
        for g in search:
            computers.append (g[0][1]["cn"][0])

        computers.sort()
        return { "computers":computers }

    def getAllComputers(self):
        computers = []
        search = self.ldap.search("cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn","uniqueIdentifier","dhcpComments","dhcpHWAddress"])
        for g in search:
            try:
                computer = {
                    "cn" : g[0][1]["cn"][0],
                    "username": g[0][1]["uniqueIdentifier"][0],
                    "serial": g[0][1]["dhcpComments"][0],
                    "mac": g[0][1]["dhcpHWAddress"][0]
                }
                computers.append (computer)
            except:
                pass

        return { "computers":computers }
