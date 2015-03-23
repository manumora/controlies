##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    Hosts.py
# Purpose:     Hosts class
# Language:    Python 2.5
# Date:        7-Feb-2011.
# Ver:        7-Feb-2011.
# Author:   Manuel Mora Gordillo
#           Francisco Mendez Palma
# Copyright:    2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#               2011 - Francisco Mendez Palma <fmendezpalma @no-spam@ gmail.com>
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
import applications.controlies.modules.NetworkUtils as NetworkUtils

class Hosts(object):

    def __init__(self):
        pass
    
    def __init__(self,ldap,name,ip,mac,type_host):
        self.ldap = ldap
        self.name = name
        self.ip = ip
        self.mac = mac
        self.type_host = type_host
        
        config = self.ldap.search("cn=DHCP Config","cn=INTERNAL",["dhcpOption"])  
        self.domainname = config[0][0][1]['dhcpOption'][4].replace('"','').replace('domain-name ','')
            
    def validation(self,action):

        if self.type_host == "none":
            return "type_host"
	
        if self.name == "":
            return "name"

        if action == "add":
            if self.existsHostname():
                return "hostAlreadyExists"
                
        if self.ip == "":
            return "ip"

        if not ValidationUtils.validIP(self.ip):
            return "ip"

        if action == "add":            
            if self.existsIP():
                return "ipAlreadyExists"
        elif action == "modify":
            if not self.equalIP():
				if self.existsIP():
					return "ipAlreadyExists"

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

        # reverse Sort
        reverseSort = False
        if args['sord'] == "asc":
            reverseSort = True        
                                
        hostnames = self.getListTriplets()
        hostnames_data = {}

        search = self.ldap.search("cn=INTERNAL,cn=DHCP Config","cn=*",["cn","dhcpHWAddress"])

        for s in search:
            if s[0][1]['cn'][0] in hostnames:
				hostnames_data[s[0][1]['cn'][0]] = {"mac" : s[0][1]['dhcpHWAddress'][0].replace("ethernet ",""), "host":s[0][1]['cn'][0]}						
        
        search = self.ldap.search("dc="+self.domainname+",ou=hosts","dc=*",["dc","aRecord"])
        for s in search:
            if s[0][1]['dc'][0] in hostnames_data:			
				if s[0][1]['dc'][0] in hostnames:
					hostnames_data[s[0][1]['dc'][0]]["ip"] = s[0][1]['aRecord'][0]

        rows = []

        try:
            host_search = args["cn"] or ""
        except:
            host_search = ""
            
        try:
            ip_search = args["ipHostNumber"] or ""
        except:
            ip_search = ""

        try:
            mac_search = args["macAddress"] or ""
        except:
            mac_search = ""

        for k, v in hostnames_data.iteritems():
            try:
				host = v["host"]
            except:
				host = ""

            try:
				ip = v["ip"]
            except:
				ip = ""

            try:
				mac = v["mac"]
            except:
				mac = ""

            if ((ip_search != "" and ip.find(ip_search)>=0) or (ip_search=="")) and ((mac_search != "" and mac.find(mac_search)>=0) or (mac_search=="")) and ((host_search != "" and host.find(host_search)>=0) or (host_search=="")):
				row = {
					"id":host, 
					"cell":[host, ip, mac],
					"cn":host,
					"ipHostNumber":ip,
					"macAddress":mac
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
        return { "page":page, "total":totalPages, "records":len(rows), "rows":result[start:finish]  }       
        

    def add(self):
        # Hosts
        """attr = [
        ('objectclass', ['top','organizationalRole','domainRelatedObject','ipHost','ieee802Device']),
        ('associatedDomain', [self.domainname]),
        ('cn', [self.name]),
        ('macAddress', [self.mac]), 
        ('ipHostNumber', [self.ip])
        ]
        self.ldap.add("cn="+self.name+",ou=Hosts", attr)"""

        # Hosts->domain
        attr = [
        ('objectclass', ['dNSDomain2','domainRelatedObject']),
        ('associatedDomain', [self.name+'.'+self.domainname]),
        ('dc', [self.name]), 
        ('aRecord', [self.ip])
        ]
        self.ldap.add("dc="+self.name+",dc="+self.domainname+",ou=Hosts", attr)

        # Hosts->arpa->in-addr->172
        ip = self.ip.split(".")
        attr = [
        ('objectclass', ['top','dNSDomain2','domainRelatedObject']),
        ('associatedDomain', [ip[3]+"."+ip[2]+"."+ip[1]+"."+ip[0]+".in-addr.arpa"]),
        ('dc', [ip[3]]), 
        ('pTRRecord', [self.name+"."+self.domainname])
        ]
        self.ldap.add("dc="+ip[3]+",dc="+ip[2]+",dc="+ip[1]+",dc="+ip[0]+",dc=in-addr,dc=arpa,ou=Hosts", attr)

		# DHCP Config
        attr = [
        ('objectclass', ['top','dhcpHost']),
        ('dhcpStatements', ['fixed-address '+self.name]),
        ('cn', [self.name]), 
        ('dhcpHWAddress', ['ethernet '+self.mac])
        ]
        self.ldap.add("cn="+self.name+",cn=group1,cn=INTERNAL,cn=DHCP Config", attr)

        # Netgroup            
        triplets = self.getTriplets()
        triplets.append('('+self.name+',-,-)')
        triplets.sort()
        attr = [(ldap.MOD_REPLACE, 'nisNetgroupTriple', triplets )]
        self.ldap.modify("cn="+self.type_host+",ou=Netgroup", attr)
            
        return "OK"
        
    def modify(self):
        # Hosts
        """attr = [
        (ldap.MOD_REPLACE, 'ipHostNumber', [self.ip] ),
        (ldap.MOD_REPLACE, 'macAddress', [self.mac])
        ]
        self.ldap.modify("cn="+self.name+",ou=Hosts", attr)"""

        # Hosts->arpa->in-addr->172
        if not self.equalIP():
            myIP = self.getIP()
            if myIP != "":
				ip = myIP.split(".")
				self.ldap.delete("dc="+ip[3]+",dc="+ip[2]+",dc="+ip[1]+",dc="+ip[0]+",dc=in-addr,dc=arpa,ou=Hosts")
				
				ip = self.ip.split(".")
				attr = [
				('objectclass', ['top','dNSDomain2','domainRelatedObject']),
				('associatedDomain', [ip[3]+"."+ip[2]+"."+ip[1]+"."+ip[0]+".in-addr.arpa"]),
				('dc', [ip[3]]), 
				('pTRRecord', [self.name+"."+self.domainname])
				]
				self.ldap.add("dc="+ip[3]+",dc="+ip[2]+",dc="+ip[1]+",dc="+ip[0]+",dc=in-addr,dc=arpa,ou=Hosts", attr)
				
        # Hosts->domain
        attr = [(ldap.MOD_REPLACE, 'aRecord', [self.ip] )]
        self.ldap.modify("dc="+self.name+",dc="+self.domainname+",ou=Hosts", attr)

        # DHCP Config
        attr = [(ldap.MOD_REPLACE, 'dhcpHWAddress', ['ethernet '+self.mac] )]
        self.ldap.modify("cn="+self.name+",cn=group1,cn=INTERNAL,cn=DHCP Config", attr)

        return "OK"

    def delete(self):
        self.ldap.delete("cn="+self.name+",ou=Hosts")
        self.ldap.delete("cn="+self.name+",cn=group1,cn=INTERNAL,cn=DHCP Config")

        #Hosts->arpa
        myIP = self.getIP()
        if myIP != "":
            ip = myIP.split(".")
            self.ldap.delete("dc="+ip[3]+",dc="+ip[2]+",dc="+ip[1]+",dc="+ip[0]+",dc=in-addr,dc=arpa,ou=Hosts")

        self.ldap.delete("dc="+self.name+",dc="+self.domainname+",ou=Hosts")
            
        # Netgroup            
        triplets = self.getTriplets()
        triplets.remove('('+self.name+',-,-)')
        triplets.sort()
            
        attr = [(ldap.MOD_REPLACE, 'nisNetgroupTriple', triplets )]
        self.ldap.modify("cn="+self.type_host+",ou=Netgroup", attr)

        return "OK"     

    def wakeup(self,broadcast):
        NetworkUtils.startup(self.getMAC(),broadcast)
    
    def existsHostname(self):
        if self.name in self.getListTriplets():
            return True
        
        return False
        
    def existsMAC(self):
        search = self.ldap.search("cn=INTERNAL,cn=DHCP Config","cn=*",["cn","dhcpHWAddress"])
        
        for s in search:
			try:
				if s[0][1]["dhcpHWAddress"][0].replace("ethernet ","") == self.mac:
					return True
			except:
				pass

        return False


    def existsIP (self):
        # Cojo las ips de la rama hosts -> arpa -> in-addr
        result = self.ldap.search ("dc=172,dc=in-addr,dc=arpa,ou=hosts", "dc=*",["associatedDomain"])
        
        myIP = self.ip.split (".")

        for i in range (0, len (result) -1):
            reverseIP = result [i][0][1]['associatedDomain'][0].replace (".in-addr.arpa","").split(".")
            reverseIP.reverse() 
            if myIP == reverseIP:
                return True
        
        return False

    def equalMAC(self):
        if self.getMAC() == self.mac:
            return True
        
        return False

    def equalIP(self):                
        if self.getIP() == self.ip:
            return True
        
        return False
        

    def getName (self):
        return self.mac   

        
    def getInternalGroups (self):
        
        groups = []
        search = self.ldap.search("cn=INTERNAL,cn=DHCP Config","cn=group*",["cn"])
        
        for g in search:
            groups.append (g[0][1]["cn"][0])
            
        return { "groups":groups }      

    def getTriplets(self):
        triplets = self.ldap.search("ou=Netgroup","cn="+self.type_host+"",["nisNetgroupTriple"])
        triplets = triplets [0][0][1]["nisNetgroupTriple"]
        return triplets

    def getListTriplets(self):
        hostnames = []		
        triplets = self.ldap.search("ou=Netgroup","cn="+self.type_host+"",["nisNetgroupTriple"])
        triplets = triplets [0][0][1]["nisNetgroupTriple"]
        
        for t in triplets:
            hostnames.append(t.replace("(","").replace(",-,-)",""))
        return hostnames
            
    def getHostData(self):

        dataHost = {
            "cn":self.name,
            "mac":self.getMAC(),
            "ip":self.getIP()
        }
        return dataHost             

    def getIP(self):
        search = self.ldap.search("dc="+self.domainname+",ou=hosts","dc="+self.name,["dc","aRecord"])
        ip=""
        try:
            ip = search[0][0][1]["aRecord"][0]
        except:
            pass
        return ip

    def getMAC(self):
        search = self.ldap.search("cn=INTERNAL,cn=DHCP Config","cn="+self.name,["cn","dhcpHWAddress"])
        mac = search[0][0][1]["dhcpHWAddress"][0].replace("ethernet ","")        
        return mac

    def getLTSPStatus (self):
        from Utils.avahiClient import avahiClient
        import threading
        
        a = avahiClient()  
        a.start() 
        time.sleep(1000)    
        a.cancel()      
        names = a.getList()
        print names
        
        """a = avahiClient()
        time.sleep(1000)        
        names = a.getList()
        print names
        a.kill()"""
        return names

#   def wakeup(self):
#       from twisted.internet.task import LoopingCall
#       from twisted.internet import defer
#       from Plugins import NetworkUtils
#       NetworkUtils.startup(self.mac)
        

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
