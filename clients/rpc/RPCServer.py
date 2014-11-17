#!/usr/bin/env python
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      RPCServer.py
# Purpose:     RPC Server for clients
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
import socket, os, time
import subprocess
import struct
from netifaces import interfaces, ifaddresses, AF_INET

class XMLRPCServer(SimpleXMLRPCServer):
    
    def process_request(self, request, client_address):

       self.client_address = client_address[0]
       return SimpleXMLRPCServer.process_request(self, request, client_address)
       
#Esto es una barbaridad, ya que accedemos a un atributo de un objeto global,
#pero es la unica manera de hacerlo para averiguar el origen de la peticion.
#Nos basamos en que:
#   1) SimpleXMLRPCServer no procesa varias peticiones a la vez, hasta que
#      no acaba una no hace caso de las siguientes. De esta manera, el client_address
#      mantiene la IP de la peticion en curso.
#   2) Desde las funciones registradas es imposible saber el objeto SimpleXMLRPCServer
#      que ha hecho la llamada, por tanto tenemos que accederlo como variable global, ya
#      que en nuestro servidor RPC solo hay un objeto de esta clase.

#Retorna la direccion IP origen de la peticion actualmente cursada por el servidor.
def getIPRequest():
    global server    
    return server.client_address

#Retorna la direccion IP del servidor ldap del centro.
def getLdapIP():
    global ldap_ip
    return ldap_ip

#Determina si la peticion proviene desde el servidor ldap    
def desdeLdap():
  
    return True if getIPRequest() == getLdapIP() else False

#Determina si la peticion proviene desde la red interna del aula (192.168.*)
def desdeRedInterna():
    
    ip=getIPRequest()
    return True if ip[0:8] == "192.168." else False
        
def getDomain():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dom ='sindominio'
	try:
		s.connect(("servidor", 0))
		inet_address= s.getsockname()[0]
		nombre=socket.gethostbyname_ex(socket.gethostname())[0].split(".")
		if len(nombre)>1:
			dom=nombre[1]
	except:
		pass

	return dom

def getIP():
    active = ""
	ignore = ['lo','pan0']
	for ifaceName in interfaces():
		if ifaceName not in ignore:
			address = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'NoIP'}] )]
			if address[0].startswith("172."):
				active=address[0]
	return active

def getNumUsers():
	p = subprocess.Popen(["who"], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["wc","-l"], stdin=p.stdout, stdout=subprocess.PIPE).communicate()[0]
	return p2

def getHostName():
    global host_name
    if desdeRedInterna():
        output=host_name
    else:
        output="No autorizado"
    return output

def ping():
    
    return "pong"

def shutdown():
    if desdeLdap() :
        num = getNumUsers()
        if num == 0:
                try:
                        process = subprocess.Popen(["init","0"], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
                        output, error = process.communicate()
                        if error!="":
                                output = error
                except:
                        output = "Error al procesar el comando"
        else:
            output="No se pudo apagar, hay usuarios logueados"
    else:
        output="No autorizado"    
    return output

def wakeupThinclients(addresses):
    
    if desdeLdap() :
        output=""
        for address in addresses:
                try:
                        addr_byte = address['dhcpHWAddress'].split(':')
                        hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
                        int(addr_byte[1], 16),
                        int(addr_byte[2], 16),
                        int(addr_byte[3], 16),
                        int(addr_byte[4], 16),
                        int(addr_byte[5], 16))

                        msg = '\xff' * 6 + hw_addr * 16

                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                        try:
                                s.sendto(msg, ('<broadcast>', 9))
                                s.sendto(msg, ('<broadcast>', 7))
                                s.sendto(msg, ('192.168.0.255', 9))
                                s.sendto(msg, ('192.168.0.255', 7))
                        except:
                                s.sendto(msg, ('<broadcast>', 2000))
                                s.sendto(msg, ('192.168.0.255', 2000))
                        s.close()
                        output = output + address['cn']+" ("+address['dhcpHWAddress']+") - <span style='color:green; font-weight:bold;'>OK</span><br/>"
                except:
                        output = output + address['cn']+" ("+address['dhcpHWAddress']+") - <span style='color:red; font-weight:bold;'>Hubo un error</span><br/>"
    else:
        output="No autorizado"    
    return output

def exec_command (command):
    try:
        if desdeLdap() :
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
            output, error = process.communicate()
            if error!="":
                output = error
        else:
            output="No autorizado"
    except:
        output = "Error al procesar el comando"
    return output

IP = getIP()
if IP!="":
	server = XMLRPCServer (("", 6800))
	ldap_ip=socket.gethostbyname("ldap")
	host_name=socket.gethostname()
	server.register_function (exec_command)
	server.register_function (shutdown)
	server.register_function (wakeupThinclients)
	server.register_function (ping)
	server.register_function (getHostName)
	server.serve_forever ()
