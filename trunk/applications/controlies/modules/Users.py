##############################################################################
# -*- coding: utf-8 -*-
# Project:      ControlIES
# Module:       Users.py
# Purpose:      Users class
# Language:     Python 2.5
# Date:         7-Feb-2011.
# Ver:          7-Feb-2011.
# Author:       Manuel Mora Gordillo
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
import hashlib
import base64
from math import floor
from operator import itemgetter
from Utils import Utils, LdapUtils

class Users(object):

    def __init__(self):
        pass
    
    def __init__(self,ldap,type,name,surname,nif,user,password,password2,departments,classrooms,foto=None):
        self.ldap = ldap
        self.type = type
        self.name = name
        self.surname = surname
        self.nif = nif
        self.user = user        
        self.password = password
        self.password2 = password2
        self.departments = departments
        self.classrooms = classrooms
        self.foto=foto
        if  self.departments.__class__.__name__ == 'str': self.departments=[departments]
        if  self.classrooms.__class__.__name__ == 'str': self.classrooms=[classrooms]
        
        
    def validation(self,action):
        
        if action == "add":
            if self.type == "none":
                return "type"
        
        if self.name == "":
            return "name"

        if self.nif == "":
            return "nif"

        if self.user == "":
            return "user"
        
        if action == "add":
            if self.existsUsername():
                return "userAlreadyExists"
        
            if self.password == "":
                return "password"

            if self.password2 == "":
                return "password2"

            if self.password != self.password2:
                return "distinctPassword"
                
        elif action == "modify":            
            if self.password == "" and self.password2 != "":
                return "password"
                                
            if self.password != "" and self.password2 == "":
                return "password2"

            if self.password != "" and self.password2 != "" and self.password != self.password2:
                return "distinctPassword"

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
        search = self.ldap.search("ou=People",filter,["employeeNumber","uid","cn","uidnumber","gidnumber","homedirectory"])

        # grid parameters
        limit = int(args['rows'])
        page = int(args['page'])
        start = limit * page - limit
        finish = start + limit;             

        # sort by field
        sortBy = args['sidx']
        if sortBy == "uid":
            sortBy = "id"

        # reverse Sort
        reverseSort = False
        if args['sord'] == "asc":
            reverseSort = True

        # type of user (Teacher/Student)
        try:
            searchType = str(args['type'])
        except LookupError:
            searchType = "None"

        rows = []
        for i in search:
            typeRow="Alumno"
            userdata=i[0][1]
            if userdata["homeDirectory"][0][0:14]=="/home/profesor":
                typeRow="Profesor"
                
            if not "employeeNumber" in userdata: userdata["employeeNumber"]=["0"]

            if searchType == typeRow or searchType=="None":
                row = {
                    "id":str(userdata["uid"][0]), 
                    "cell":[typeRow, str(userdata["cn"][0]), str(userdata["uid"][0]), str(userdata["uidNumber"][0]), str(userdata["gidNumber"][0]), str(userdata["employeeNumber"][0])], 
                    "type": typeRow,                    
                    "cn":str(userdata["cn"][0]),
                    "uidNumber":str(userdata["uidNumber"][0]),
                    "gidNumber":str(userdata["gidNumber"][0]),                
                    "employeeNumber":str(userdata["employeeNumber"][0])
                }
                rows.append(row)
   
        # grid parameters
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


    def buildFilter(self, args):
        filter = "(&(uid=*)"
        try:
            if str(args['uid'])!="None":
                filter = filter + "(uid=*" + str(args['uid']) + "*)"
        except LookupError:
            pass

        try:
            if str(args['cn'])!="None":
                filter = filter + "(cn=*" + str(args['cn']) + "*)"
        except LookupError:
            pass

        try:
            if str(args['uidNumber'])!="None":
                filter = filter + "(uidNumber=" + str(args['uidNumber']) + ")"
        except LookupError:
            pass

        try:
            if str(args['gidNumber'])!="None":
                filter = filter + "(gidNumber=" + str(args['gidNumber']) + ")"
        except LookupError:
            pass

        try:
            if str(args['employeeNumber'])!="None":
                filter = filter + "(employeeNumber=*" + str(args['employeeNumber']) + "*)"
        except LookupError:
            pass

        filter = filter + ")"
        return filter


    def add(self):        

        maxID = str(LdapUtils.getMaxID(self.ldap))
        passwd = '{SSHA}' + Utils.encrypt(self.password)
        name = self.name+" "+self.surname
        
        attr = [
        ('objectclass', ['top','posixAccount','shadowAccount','person','inetOrgPerson']),
        ('uid', [self.user]),
        ('cn', [name.strip()] ),
        ('employeenumber', [self.nif] ),        
        ('sn', [name.strip()] ),
        ('uidnumber', [maxID] ),
        ('gidnumber', [maxID] ),    
        ('loginshell', ['/bin/bash'] ),
        ('homeDirectory', [LdapUtils.whatHome(self.type) + self.user] ),
        #('jpegPhoto', ['jpegPhoto'] ),     
        ('userpassword', [passwd])
        ]
        if self.foto is not None:
            attr.append(('jpegPhoto',[self.foto]))

        self.ldap.add("uid="+self.user+",ou=People", attr)

        # Add private group
        attr = [
        ('objectclass', ['top','posixGroup','lisGroup']),
        ('grouptype', ['private']), 
        ('gidnumber', [maxID] ),    
        ('cn', [self.user] ),
        ('description', [self.name+' personal group'] )
        ]

        self.ldap.add("cn="+self.user+",ou=Group", attr)
        
        
        # Add selected groups   
        attr = [
        (ldap.MOD_ADD, 'member', ['uid='+self.user+',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
        (ldap.MOD_ADD, 'memberUid', [self.user] )
        ]

        if self.departments != ['']:                   
            for n in self.departments:
                self.ldap.modify('cn='+ n +',ou=Group', attr)
    
        if self.classrooms != ['']:  
            for n in self.classrooms:
                self.ldap.modify('cn='+ n +',ou=Group', attr)
            
        if self.type=='teacher':
            self.ldap.modify('cn=teachers,ou=Group', attr)
        elif self.type=='student':
            self.ldap.modify('cn=students,ou=Group', attr)
                        
        return "OK"
            
            
    def modify(self):
        name = self.name+" "+self.surname
        
        attr = [
        (ldap.MOD_REPLACE, 'cn', [name.strip()] ),
        (ldap.MOD_REPLACE, 'employeenumber', [self.nif] ),      
        (ldap.MOD_REPLACE, 'sn', [name.strip()] )       
        ]

        if self.password!="":
            passwd = '{SSHA}' + Utils.encrypt(self.password)
            attr.append((ldap.MOD_REPLACE, 'userpassword', [passwd]))
        
        self.ldap.modify("uid="+self.user+",ou=People", attr)

        # Get current groups
        currentGroups = self.getUserGroups()
        
        groupsDepartments = Utils.cmpLists(currentGroups["departments"], self.departments)
        groupsClassrooms = Utils.cmpLists(currentGroups["classrooms"], self.classrooms)     
        
        # Delete unselected groups      
        deleteDepartments = groupsDepartments["onlyInList1"]
        deleteClassrooms = groupsClassrooms["onlyInList1"]
        
        attr = [
        (ldap.MOD_DELETE, 'member', ['uid='+self.user+',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
        (ldap.MOD_DELETE, 'memberUid', [self.user] )
        ]

        for d in deleteDepartments:
            self.ldap.modify('cn='+ d +',ou=Group', attr)

        for d in deleteClassrooms:
            self.ldap.modify('cn='+ d +',ou=Group', attr)
                    
        # Add selected groups   
        newDepartments = groupsDepartments["onlyInList2"]
        newClassrooms = groupsClassrooms["onlyInList2"]
        
        attr = [
        (ldap.MOD_ADD, 'member', ['uid='+self.user+',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
        (ldap.MOD_ADD, 'memberUid', [self.user] )
        ]

        for n in newDepartments:
            self.ldap.modify('cn='+ n +',ou=Group', attr)

        for n in newClassrooms:
            self.ldap.modify('cn='+ n +',ou=Group', attr)
                    
        return "OK"


    def delete(self):
        
        self.ldap.delete('uid='+ self.user +',ou=People')
        self.ldap.delete("cn="+self.user+",ou=Group")
        
        # Delete unselected groups      
        currentGroups = self.getUserGroups()

        attr = [
        (ldap.MOD_DELETE, 'member', ['uid='+self.user+',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
        (ldap.MOD_DELETE, 'memberUid', [self.user] )
        ]

        self.ldap.modify('cn=teachers,ou=Group', attr)
        self.ldap.modify('cn=students,ou=Group', attr)

        for d in currentGroups["departments"]:
            self.ldap.modify('cn='+ d +',ou=Group', attr)

        for d in currentGroups["classrooms"]:
            self.ldap.modify('cn='+ d +',ou=Group', attr)
            
        return "OK"


    def existsUsername(self):
        
        result = self.ldap.search("ou=People","uid="+self.user,["uid"])

        if len(result) > 0:
            return True
        
        return False


    def searchNewUsername(self):

        result = self.ldap.search("ou=People","uid=*",["uid"])
        users = []
        for i in result:
            users.append(i[0][1]['uid'][0])

        n = self.name.lower().split(" ")
        
        username = ""
        if len(n) > 0:
            username = n[0][0:1]

        if len(n) > 1:
             username = username + n[1]
             
        if len(n) > 2:
            username = username + n[2][0:1]

        num = 1
        searching = username + "0" + str(num)

        found = True
        while found:
            try:
                users.index(searching)
                num = num + 1
                
                if len(str(num)) == 1:
                    searching = username + "0" + str(num)
                else:
                    searching = username + str(num)
            except:
                found = False
                
        return searching

    def getUserGroups(self):
        result = self.ldap.search("ou=Group","(&(memberUid="+str(self.user)+")(|(groupType=school_department)(groupType=school_class)))",["cn","groupType"])

        departments = []
        classrooms = []     
        for g in result:
            if g[0][1]["groupType"][0] == "school_department":
                departments.append(g[0][1]["cn"][0])
            elif g[0][1]["groupType"][0] == "school_class":
                classrooms.append(g[0][1]["cn"][0])
        
        departments.sort()
        classrooms.sort()
        return { "departments":departments, "classrooms":classrooms }
        
    def getUserData(self):
        self.getUserGroups()
        result = self.ldap.search("ou=People","uid="+str(self.user),["uid","cn","sn","employeenumber","homedirectory","uidnumber","gidnumber","jpegPhoto"])
        
        if len(result) == 0:
            return { "user":"", "name":"", "surname":"", "nif":"", "photo":"", "type":"","uidnumber":"","gidnumber":"", "groups":[] }
        
        type = "student"
        if result[0][0][1]["homeDirectory"][0][0:14]=="/home/profesor":
            type = "teacher"
        
        try:
            photo = base64.b64encode(result[0][0][1]["jpegPhoto"][0])
        except:
            photo = ""
        userdata=result[0][0][1]  
        if "employeeNumber" not in userdata: userdata["employeeNumber"]=["0"]
        dataUser = {
            "user":userdata["uid"][0],
            "name":userdata["cn"][0],
            "surname":userdata["sn"][0],
            "nif":userdata["employeeNumber"][0],
            "uidnumber":userdata["uidNumber"][0],
            "gidnumber":userdata["gidNumber"][0],
            "photo":photo,
            "type":type,
            "groups":self.getUserGroups()
         }
         
        return dataUser

    def getUserPhoto(self):
        self.getUserGroups()
        result = self.ldap.search("ou=People","uid="+self.user,["jpegPhoto"])
                
        try:
            photo = base64.b64encode(result[0][0][1]["jpegPhoto"][0])
        except:
            photo = ""
            
        dataUser = {
            "photo":photo
         }
         
        return dataUser
