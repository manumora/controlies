##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    LdapUtils.py
# Purpose:     Ldap utils
# Language:    Python 2.5
# Date:        18-Feb-2011.
# Ver:        18-Feb-2011.
# Author:	Manuel Mora Gordillo
#			Francisco Mendez Palma
# Copyright:    2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#				2011 - Francisco Mendez Palma <fmendezpalma @no-spam@ gmail.com>
#               2011 - José L. Redrejo Rodríguez <jredrejo @no-spam@ debian.org>
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

# Get all users
def getAllUsers(ldap):
	result = ldap.search("ou=People","uid=*",["uid","cn"])

	rows = []
	for u in result:
		rows.append([u[0][1]['uid'][0] , u[0][1]['cn'][0] ]);

	return rows


# Get all groups classified by type
def getAllGroups(ldap):
	result = ldap.search("ou=Group","(|(groupType=school_department)(groupType=school_class))",["cn","groupType"])
	
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

def getClassroomGroups(ldap):
	result = ldap.search("ou=Group","(|(groupType=school_class))",["cn","groupType"])
	
	classrooms = []		
	for g in result:
		classrooms.append(g[0][1]["cn"][0])
	
	classrooms.sort()
	
	return { "classrooms":classrooms }

def getClassroomGroupsWithUsers(ldap):
	result = ldap.search("ou=Group","(|(groupType=school_class))",["cn","groupType","memberUid"])
	
	classrooms = []		
	for g in result:
		try:
			d = {g[0][1]["cn"][0]:g[0][1]["memberUid"]}
			classrooms.append(d)
		except:
			pass
	
	classrooms.sort()
	return { "classrooms":classrooms }


def getThinclientsFromClassroom(ldap,classroom):
	search = ldap.search("cn=THINCLIENTS,cn=DHCP Config","cn=*",["cn","dhcpHWAddress"])
		
	num = classroom.split("-pro")[0]
	
	rows=[]
	for i in search:
		host = i[0][1]["cn"][0]
		try:
			mac = i[0][1]["dhcpHWAddress"][0].replace("ethernet ","")
		except:
			mac = ""
		
		if mac != "" and host.startswith(num):
			row = {
				"cn":host,
				"dhcpHWAddress":mac,
			}			 
			rows.append(row)
	return rows

def getAllRanges(ldap):
	myRange = []
	mySubRange = []	
			
	my_search = ldap.search("dc=172,dc=in-addr,dc=arpa,ou=hosts","dc=*",["dc"])
	for s in my_search:
		address = s[0][0].split(",")
		if len(address) == 9:
			myRange.append(address[0].replace("dc=",""))
			
		if len(address) == 8:
			mySubRange.append(address[0].replace("dc=",""))

	myRange.sort()
	mySubRange.sort()
	return { "ranges":myRange, "subrange":mySubRange }

# Get the max ID of the groups and users
def getMaxID(ldap): 
    		
    result = ldap.search("ou=Group","cn=*",["gidNumber"])
    numbers1 = [int(i[0][1]['gidNumber'][0]) for i in result]
        
    result = ldap.search("ou=People","uid=*",["gidNumber","uidNumber"])	
    numbers2=[int(i[0][1]['gidNumber'][0]) for i in result]
    numbers3=[int(i[0][1]['uidNumber'][0]) for i in result]
    numbers=numbers1 + numbers2 + numbers3

    numbers.sort()		

    maxID = 1		
    if len(numbers) > 0:
        maxID = numbers[-1:][0] + 1

    return maxID

def getBroadcast(ldap):
	result = ldap.search("cn=DHCP Config","cn=INTERNAL",["dhcpOption"])

	record = [i for i in result[0][0][1]['dhcpOption'] if i.startswith('broadcast')]
	try:
		broadcast =record[0].split(" ")[1]
	except:
		broadcast=""

	return broadcast
	
def whatHome(type):
	
	if type == "teacher":
		return "/home/profesor/"
	else:
		return "/home/alumnos/"

def clean_teachers(ldap_con):
    """vaciado los grupos de profesores"""
    cadena="(cn=teachers)"
    clean_group(cadena,ldap_con)    
    cadena="(groupType=school_department)"
    clean_group(cadena,ldap_con)
    
def clean_students(ldap_con):
    cadena="(cn=students)"
    clean_group(cadena,ldap_con)   
    cadena="(groupType=school_class)"    
    clean_group(cadena,ldap_con)

    
def clean_group(tipo_grupo,ldap_con):
    """vaciado de los grupos"""
    import ldap
    import ldap.modlist

    result = ldap_con.search("ou=Group",tipo_grupo,["member","memberUid","cn"])
    if result is not None:
        for grupo in result:
            dn="cn="+ grupo[0][1]['cn'][0] + ",ou=Group"
            attr_viejo=grupo[0][1]
            attr_nuevo={'member':[''],'memberUid':[''],'cn':grupo[0][1]['cn']}
            modificacion=ldap.modlist.modifyModlist(attr_viejo,attr_nuevo)
            ldap_con.modify(dn, modificacion)


def sanea_grupos(ldap_con):
    """borrar de los grupos usuarios que ya no existen"""
    import ldap
    import ldap.modlist    
    tipos=('school_class','school_department')
    grupos=['teachers','students']
    
    #obtengo todos los grupos
    for tipo in tipos:
        result=ldap_con.search('ou=Group','groupType=' + tipo,['cn'])
        if len(result)>0:
            for i in result:
                grupos.append(i[0][1]['cn'][0])
                
    #en cada grupo borro usuarios     
    for grupo in grupos:
        result=ldap_con.search('ou=Group','cn=' + grupo,['memberUid','member'])
        if len(result)>0:
            listado=result[0][0][1]['memberUid']
            listado_members=result[0][0][1]['member']
            modificar=False
            for usuario in listado:
                if usuario!='':
                    existe=len(ldap_con.search('ou=People','uid=' + usuario,['cn']))>0
                    if not existe:
                        modificar=True
                        listado.remove(usuario)
                        listado_members.remove('uid=' + usuario + ',ou=People,dc=instituto,dc=extremadura,dc=es')

            if modificar:
                attr_viejo=ldap_con.search('ou=Group','cn=' + grupo,['memberUid','member'])[0][0][1]
                attr_nuevo={'member':listado_members,'memberUid':listado}
                dn="cn="+ grupo + ",ou=Group"
                modificacion=ldap.modlist.modifyModlist(attr_viejo,attr_nuevo)
                ldap_con.modify(dn, modificacion)                

