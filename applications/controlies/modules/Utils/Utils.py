##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    Groups.py
# Purpose:     Groups class
# Language:    Python 2.5
# Date:        18-Feb-2011.
# Ver:        18-Feb-2011.
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

def cmpLists(list1, list2):
	
	onlyInList1 = set(list1).difference(set(list2))
	onlyInList2 = set(list2).difference(set(list1))
	inTwoLists = set(list1) & set(list2)

	return { 'onlyInList1':onlyInList1, 'onlyInList2':onlyInList2, 'inTwoLists':inTwoLists }


def parseToLdap(string):
	string = string.replace(" ","_")
	string = string.replace("á","a").replace("é","e").replace("í","o").replace("ó","o").replace("ú","u")
	string = string.replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")	
	string = string.replace("ñ","n").replace("Ñ","N")
				
	return string

def generate_salt():
	# Salt can be any length, but not more than about 37 characters
	# because of limitations of the binascii module.
	# 7 is what Netscape's example used and should be enough.
	# All 256 characters are available.
	from random import randrange
	
	salt = ''
	for n in range(7):
		salt += chr(randrange(256))
	return salt

def encrypt(password):
	import sha
	from binascii import b2a_base64
	
	password = str(password)
	salt = generate_salt()
 
	return b2a_base64(sha.new(password + salt).digest() + salt)[:-1]

def generateRSAkeys(_path):
	import os
	from M2Crypto import RSA            

	ssh_dir = _path + '/.ssh'

	if os.path.isdir(ssh_dir):
		os.chmod(ssh_dir,0700)
	else:
		os.mkdir(ssh_dir,0700)

	key = RSA.gen_key(2048, 65537)
	key.save_pem(ssh_dir+'/id_rsa',cipher=None)
	os.chmod(ssh_dir+'/id_rsa',0600)

	os.system("ssh-keygen -y -f "+ssh_dir+'/id_rsa > '+ssh_dir+'/id_rsa.pub')

def homeDirectory(_type):
	if _type == "teacher":
		homeDirectory = "/home/profesor/"
	else:
		homeDirectory = "/home/alumnos/"
		
	return homeDirectory