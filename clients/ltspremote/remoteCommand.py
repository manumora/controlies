#!/usr/bin/python
# coding: utf8
##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      avahiClientLTSP.py
# Purpose:     Avahi Client in Classroom network
# Language:    Python 2.5
# Date:        26-Oct-2011.
# Ver:        26-Oct-2011.
# Author:	Manuel Mora Gordillo
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

import sys
from SSHConnection import SSHConnection
import websocket_messaging as WS
import ansi
from ansi2html import ansi2html

def executeCommand(host, command, hostname):
	c = SSHConnection(host,"root","")
	response = c.connectWithoutPass("/usr/share/controlies-ltspserver/.ssh/id_rsa")

	try:
		WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+hostname+'</span> > <span style="font-size:10pt;">'+command+'</span><br>','mykey','mygroup')
	except:
		#return dict(response="fail", host=host, message="No se pudo conectar con el servidor websocket.<br/>")
		print "no_websocket"
		sys.exit(0)
	    
	if response != True:
		print "no_ssh"
		sys.exit(0)
		#return dict(response="fail", host=host, message="No se pudo conectar. ¿Está encendido el equipo? ¿Has establecido la relación de confianza?<br/>")

	channel = c.exec_command(command)
	import select

	while True:
		if channel.exit_status_ready():
			break
		rl, wl, xl = select.select([channel], [], [], 0.0)
		if len(rl) > 0:

			stdout_data = []
			try:
			    part = channel.recv(4096)
			    while part:
				stdout_data.append(part)
				part = channel.recv(4096)
			except:
			    raise

			complete = ''.join(stdout_data)

			n = 500
			pieces = [complete[i:i+n] for i in range(0, len(complete), n)]

			HTML_PARSER = ansi2html()
			for i in pieces:
				html = HTML_PARSER.parse(i)			
				try:        
					WS.websocket_send('http://ldap:8888',html,'mykey','mygroup')
				except:
					pass

	channel.close()
	c.close()

if __name__ == "__main__":
	executeCommand(sys.argv[1], sys.argv[2], sys.argv[3])
	sys.exit(0)
