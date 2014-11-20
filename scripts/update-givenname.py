#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
# Project:      ControlIES
# Module:    	update-givenname.py
# Purpose:     	Update given name and surname
# Language:    	Python 2.5
# Date:        	31-Oct-2014.
# Ver:         	31-Oct-2014.
# Author:    	Manuel Mora Gordillo
# Copyright:    2014 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
# Description:
#	- Motivo: Almacenar por separado el nombre y apellidos de cada usuario.
#	- Parámetro: password de LDAP (python update-givenname.py passLDAP)
#       - Uso: colocar previamente en el mismo directorio del script los ficheros
#              ExportacionDatosProfesorado.xml y Alumnos.xml (al menos uno de ellos)
#
# ControlIES is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ControlIES is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
##############################################################################

import ldap
import sys, os
import xml.dom.minidom

class LdapConnection(object):

    def __init__(self,host,username,password):
		self.host = host
		self.username = username
		self.password = password

    def connectauth(self):
    	self.connectauth = ldap.open (self.host)
    	try:
	        self.protocol_version = ldap.VERSION3
	        self.connectauth.simple_bind_s(self.username, self.password)
    	except ldap.CONFIDENTIALITY_REQUIRED:
    		try:
			ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                	self.connectauth=ldap.initialize("ldaps://" +self.host+":636")
			self.connectauth.set_option(ldap.OPT_REFERRALS, 0)
			self.connectauth.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
			self.connectauth.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
			self.connectauth.set_option( ldap.OPT_X_TLS_DEMAND, True )
			self.connectauth.set_option( ldap.OPT_DEBUG_LEVEL, 255 )

                	self.connectauth.simple_bind_s(self.username,self.password)
                	return True
            	except ldap.LDAPError,e:
                	return False

	return True


    def search(self,baseDN,filter,retrieveAttributes):
		try:
			ldap_result_id = self.connectauth.search(baseDN+",dc=instituto,dc=extremadura,dc=es", ldap.SCOPE_SUBTREE, filter, retrieveAttributes)
			result_set = []
			while 1:
				result_type, result_data = self.connectauth.result(ldap_result_id, 0)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)
			return result_set
		except ldap.LDAPError, e:
			print e

    def modify(self,baseDN,attr):
        try:
            self.connectauth.modify_s(baseDN+",dc=instituto,dc=extremadura,dc=es", attr)
            
        except ldap.OPERATIONS_ERROR:
            print "error"
        except ldap.NO_SUCH_OBJECT:
            print "no_such_object"
        except Exception,e:
            print e
            
        return True

###################################################################################################################################################

def asegura_codigos(cadena):
	resultado = cadena.replace(u"á", u"a")
	resultado = resultado.replace(u"Á", u"A")
	resultado = resultado.replace(u"à", u"a")
	resultado = resultado.replace(u"ä", u"a")
	resultado = resultado.replace(u"À", u"A")
	resultado = resultado.replace(u"Ä", u"A")        
	resultado = resultado.replace(u"é", u"e")
	resultado = resultado.replace(u"ë", u"e")        
	resultado = resultado.replace(u"É", u"E")
	resultado = resultado.replace(u"Ë", u"E")        
	resultado = resultado.replace(u"è", u"e")
	resultado = resultado.replace(u"È", u"E")
	resultado = resultado.replace(u"í", u"i")
	resultado = resultado.replace(u"Í", u"I")
	resultado = resultado.replace(u"ì", u"i")
	resultado = resultado.replace(u"ï", u"i")        
	resultado = resultado.replace(u"Ì", u"I")
	resultado = resultado.replace(u"Ï", u"I")        
	resultado = resultado.replace(u"ó", u"o")
	resultado = resultado.replace(u"Ó", u"O")
	resultado = resultado.replace(u"Ö", u"O")
	resultado = resultado.replace(u"ò", u"o")
	resultado = resultado.replace(u"ö", u"o")        
	resultado = resultado.replace(u"Ò", u"O")
	resultado = resultado.replace(u"ú", u"u")
	resultado = resultado.replace(u"Ú", u"U")
	resultado = resultado.replace(u"ü", u"u")
	resultado = resultado.replace(u"Ü", u"U")
	resultado = resultado.replace(u"ù", u"u")
	resultado = resultado.replace(u"Ù", u"U")
	resultado = resultado.replace(u"ª", u"a")
	resultado = resultado.replace(u"º", u"o")
	resultado = resultado.replace(u"ñ", u"n")
	resultado = resultado.replace(u"Ñ", u"N")
	resultado = resultado.replace(u"ç", u"c")
	resultado = resultado.replace(u"(", u"")
	resultado = resultado.replace(u")", u"")    
	resultado = resultado.replace(u".", u"")
	resultado = resultado.replace(u",", u"")  
	resultado = resultado.replace(u"&", u"")
	return str(resultado).strip()


def parse_nodo(nodo):
	usuario={}

	for info in nodo.childNodes: 
	    if info.nodeType!=info.TEXT_NODE:
		try:
			dato=info.firstChild.nodeValue                    
		except : # no hay dato en este nodo, p. ej. segundo-apellido
			dato=' '            

		if info.nodeName == 'nie':
		    usuario["dni"]=asegura_codigos(dato)		                       
		else:
		    usuario[info.nodeName]=asegura_codigos(dato)

	usuarios.append(usuario)


def parsea_archivo(archivo_xml,tipo):
	xml_usuarios=xml.dom.minidom.parse(archivo_xml)
	lista= xml_usuarios.getElementsByTagName(tipo)

	for nodo in lista:
		parse_nodo(nodo)

def modify_user(user, name, surname):
	cn = name+" "+surname

	attr = [
	(ldap.MOD_REPLACE, 'cn', [cn.strip()] ),
	(ldap.MOD_REPLACE, 'givenName', [name] ),
	(ldap.MOD_REPLACE, 'sn', [surname] )       
	]

	l.modify("uid="+user+",ou=People", attr)
	print "Modificando: "+user

##############################################################################################################################################

if __name__ == '__main__':
	usuarios=[]

	if len(sys.argv) != 2:
		print "Debe proporcionar la contraseña LDAP: "+sys.argv[0]+" password_LDAP";

	l = LdapConnection("ldap", "cn=admin,ou=People,dc=instituto,dc=extremadura,dc=es", sys.argv[1])
	if not l.connectauth():
		print "Contraseña LDAP incorrecta"
		exit()

	if not os.path.exists("Alumnos.xml"):
		print "No existe el archivo Alumnos.xml"
	else:
		parsea_archivo("Alumnos.xml","alumno")

	if not os.path.exists("ExportacionDatosProfesorado.xml"):
		print "No existe el archivo ExportacionDatosProfesorado.xml"
	else:
		parsea_archivo("ExportacionDatosProfesorado.xml","profesor")

	search  = l.search("ou=People","(uid=*)",["uid","employeeNumber"])
	for s in search:
		for u in usuarios:
			if s[0][1]['employeeNumber'][0]==u["dni"]:
				modify_user(s[0][1]['uid'][0], u["nombre"], u["primer-apellido"]+" "+u["segundo-apellido"])

