##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    Groups.py
# Purpose:     Groups class
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
# along with ControlIES. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import ldap
import logging
from math import floor
from operator import itemgetter
from Utils import Utils, LdapUtils
from applications.controlies.modules.Users import Users

class Groups(object):

    def __init__(self):
		pass
	
    def __init__(self,ldap,type,name,users):
		self.ldap = ldap
		self.type = type
		self.name = Utils.parseToLdap(name)
		self.users = users

    def exists_group_name(self):
        
        result = self.ldap.search("ou=Group","cn="+self.name,["cn"])

        if len(result) > 0:
            return True
        
        return False
        		
    def validation(self,action):

		if self.type == "none":
			return "type"
				
		if self.name == "":
			return "name"
			
		if self.users == "":
			return "users"
					
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
			
    def list(self,args):
		filter = self.buildFilter(args)		
		search = self.ldap.search("ou=Group",filter,["cn","gidNumber","groupType","memberUid"])

		# grid parameters
		limit = int(args['rows'])
		page = int(args['page'])
		start = limit * page - limit
		finish = start + limit;				

		# sort by field
		sortBy = args['sidx']
		if sortBy == "cn":
			sortBy = "id"

		# reverse Sort
		reverseSort = False
		if args['sord']== "asc":
			reverseSort = True

		# type of group (Classroom/Department)
		try:
			searchType = str(args['type'])
		except LookupError:
			searchType = "None"

		rows = []
		for i in search:
			
			typeRow="Aula"
			if str(i[0][1]["groupType"][0])=="school_department":
				typeRow="Departamento"

			if searchType == typeRow or searchType=="None":
				try:
					list2 = [x for x in i[0][1]["memberUid"] if x]
					usersNumber = len(list2)
				except:
					usersNumber = 0

				row = {
					"id":i[0][1]["cn"][0], 
					"cell":[typeRow, i[0][1]["cn"][0], i[0][1]["gidNumber"][0], usersNumber],
					"type": typeRow,
					"cn": i[0][1]["cn"][0],
					"gidNumber": i[0][1]["gidNumber"][0],
					"usersNumber": usersNumber
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

		# sort rows
		result = sorted(rows, key=itemgetter(sortBy), reverse=reverseSort)

		return { "page":page, "total":totalPages, "records":len(rows), "rows":result[start:finish] }
		

    def listUsers(self,args):
		# grid parameters
		limit = int(args['rows'])
		page = int(args['page'])
		start = limit * page - limit
		finish = start + limit;				

		# sort by field
		sortBy = args['sidx']

		# reverse Sort
		reverseSort = False
		if args['sord']== "asc":
			reverseSort = True

		groupData = self.getGroupData()

		rows = []
		for i in groupData["memberuid"]:
			if i=="": continue

			u = Users(self.ldap,"","","","",i,"","","","")
			userData = u.getUserData()
			row = {
				"id":userData["user"], 
				"cell":[userData["surname"]+", "+userData["name"],userData["user"],userData["nif"]],
				"cn": userData["surname"]+", "+userData["name"],
				"uid": userData["user"],
				"employeeNumber": userData["nif"]
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

		# sort rows
		result = sorted(rows, key=itemgetter(sortBy), reverse=reverseSort)
		return { "page":page, "total":totalPages, "records":len(groupData["memberuid"]), "rows":result[start:finish] }



    def buildFilter(self, args):
        
        if self.type=="":
            filter = "(&(cn=*)(|(groupType=school_class)(groupType=school_department))"
        else:
            filter = "(&(cn=*)(|(groupType="+str(self.type)+"))"

        try:
            if str(args['cn'])!="None":
			filter = filter + "(cn=*" + str(args['cn']) + "*)"
        except LookupError:
            pass

        try:
            if str(args['gidNumber'])!="None":
			filter = filter + "(gidNumber=" + str(args['gidNumber']) + ")"
        except LookupError:
            pass

        filter = filter + ")"
        return filter
		

    def add(self):
        if self.exists_group_name(): return "OK"       
        maxID = str(LdapUtils.getMaxID(self.ldap))

        if len(self.users)>0:
            members = []
            for m in self.users.split(','):
                members.append("uid=" + m + ",ou=People,dc=instituto,dc=extremadura,dc=es")
            memberuids=self.users.split(',')
        else:
            members=['']
            memberuids=['']

        attr = [
        ('objectclass', ['top','posixGroup','lisGroup','lisAclGroup']),
        ('grouptype', [self.type] ),		
        ('gidnumber', [maxID] ),		
        ('cn', [self.name] ),
        ('description', [self.name+' department group']),
        ('memberuid', memberuids),
        ('member', members)
        ]

        self.ldap.add("cn="+self.name+",ou=Group", attr)

        return "OK"

			
    def modify(self):

		members = []
		for m in self.users.split(','):
			members.append("uid=" + m + ",ou=People,dc=instituto,dc=extremadura,dc=es")
			
		mod_attrs = [
		(ldap.MOD_REPLACE, 'memberuid', self.users.split(',')),
		(ldap.MOD_REPLACE, 'member', members) 
		]

		self.ldap.modify('cn='+ self.name +',ou=Group', mod_attrs)

		return "OK"


    def delete(self):
		self.ldap.delete('cn='+ self.name +',ou=Group')

		return "OK"
		

    def getGroupData(self):

		result = self.ldap.search("ou=Group","cn="+self.name,["cn","grouptype","memberuid"])

		m = result[0][0][1]["memberUid"]
		members = [x for x in m if x]
		members.sort()

		dataGroup = {
			"name":result[0][0][1]["cn"][0],
			"type":result[0][0][1]["groupType"][0],
			"memberuid":members
		 }
		 
		return dataGroup

    def getGroupUsers(self):
		result = self.ldap.search("ou=Group","cn="+self.name,["cn","memberUid"])
		members = result[0][0][1]["memberUid"]
		members.sort()

		return members

    def getGroupUsersData(self):
        groupData = self.getGroupData()

        rows = []
        for i in groupData["memberuid"]:

            u = Users(self.ldap,"","","","",i,"","","","")
            userData = u.getUserData()
            row = {
                "id":userData["user"], 
                "sn": userData["surname"]+", "+userData["name"],
                "uid": userData["user"],
                "employeeNumber": userData["nif"]
            }
            rows.append(row)

        newlist = sorted(rows, key=lambda k: k['sn']) 
        return newlist
