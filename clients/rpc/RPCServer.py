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

from SimpleXMLRPCServer import SimpleXMLRPCServer
import socket, os, time
import subprocess

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

def getNumUsers():
	p = subprocess.Popen(["who"], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["wc","-l"], stdin=p.stdout, stdout=subprocess.PIPE).communicate()[0]
	return p2

def getHostName():
	return socket.gethostname()

def ping():
	return "pong"

def shutdown():
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

	return output

def exec_command (command):
	try:
		process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
		output, error = process.communicate()
		if error!="":
			output = error
	except:
		output = "Error al procesar el comando"

	return output

server = SimpleXMLRPCServer ((getHostName(), 6800))
server.register_function (exec_command)
server.register_function (shutdown)
server.register_function (ping)
server.serve_forever ()

