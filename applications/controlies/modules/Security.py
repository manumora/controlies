##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    Security.py
# Purpose:     Authentication with ldap server
# Language:    Python 2.5
# Date:        7-Feb-2011.
# Ver:        7-Feb-2011.
# Author:    Manuel Mora Gordillo
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
# along with ControlAula. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from Plugins.LdapConnection import LdapConnection

class Security(object):

	def __init__(self,host,user,password):
		self.host = host
		self.user = user
		self.password = password


	def validation(self):
		if self.host == "":
			return "host"

		if self.user == "":
			return "user"

		if self.password == "":
			return "password"

		return "OK"

	def process(self):
		val = self.validation()
        	
		if val != "OK":
			return val

		auth = self.authentication()
		return auth

	def authentication(self):
		l = LdapConnection(self.host,'cn='+self.user+',ou=People,dc=instituto,dc=extremadura,dc=es',self.password)
		ret = l.connect()

		return ret
