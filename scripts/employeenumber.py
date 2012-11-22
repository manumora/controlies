##############################################################################
# -*- coding: utf-8 -*-
# Project:     	ControlIES
# Module:    	employeenumber.py
# Purpose:     	Añade el atributo employeenumber a los usuarios que no lo tienen
# Language:    	Python 2.5
# Date:        	25-Mar-2011.
# Ver:        	25-Mar-2011.
# Author:		Manuel Mora Gordillo
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

#Aqui el password de tu ldap
passwd = ""

connection = ldap.open("ldap")
connection.simple_bind_s("cn=admin,ou=People,dc=instituto,dc=extremadura,dc=es",passwd)

ldap_result = connection.search("ou=People,dc=instituto,dc=extremadura,dc=es", ldap.SCOPE_SUBTREE, "uid=*", ["employeeNumber","uid","cn","sn","uidNumber","gidNumber","homeDirectory","jpegPhoto","userpassword"])

result_set = []
while 1:
	result_type, result_data = connection.result(ldap_result, 0)
	if (result_data == []):
		break
	else:
		if result_type == ldap.RES_SEARCH_ENTRY:
			result_set.append(result_data)

for p in result_set:
	try:
		employeeNumber = p[0][1]['employeeNumber']
	except:
		print p[0][1]['uid'][0]+" - no tiene employeeNumber"

		try:
			jpeg = p[0][1]['jpegPhoto'][0]
		except:
			jpeg = ""
			
		attr = [
		('objectclass', ['top','posixAccount','shadowAccount','person','inetOrgPerson']),
		('uid', [p[0][1]['uid'][0]]),
		('cn', [p[0][1]['cn'][0]] ),
		('employeeNumber', [' '] ),
		('sn', [p[0][1]['sn'][0]] ),
		('uidnumber', [p[0][1]['uidNumber'][0]] ),
		('gidnumber', [p[0][1]['gidNumber'][0]] ),
		('loginshell', ['/bin/bash'] ),
		('homeDirectory', [p[0][1]['homeDirectory'][0]] ),
		('jpegPhoto', [jpeg] ),
		('userpassword', [p[0][1]['userPassword'][0]])
		]
		
		connection.delete_s("uid="+p[0][1]['uid'][0]+",ou=People,dc=instituto,dc=extremadura,dc=es")
		connection.add_s("uid="+p[0][1]['uid'][0]+",ou=People,dc=instituto,dc=extremadura,dc=es", attr)
