##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:      SSHConnection.py
# Purpose:     Connection with ssh protocol
# Language:    Python 2.5
# Date:        17-Oct-2011.
# Ver:         17-Oct-2011.
# Author:      Manuel Mora Gordillo
# Copyright:   2011 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
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

import paramiko   
    
class SSHConnection(object):
	
    def __init__(self,session):
        pass

    def __init__(self,host,user,passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        
    def validation(self):
        if self.host == "":
            return "host"

        if self.user == "":
            return "user"

        if self.passwd == "":
            return "password"

        return "OK"

    def process(self):
        val = self.validation()
            
        if val != "OK":
            return val

        auth = self.connect()
        return auth

    def connect(self):
        self.transport = paramiko.SSHClient()
        self.transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.transport.connect(self.host, username=self.user, password=self.passwd)
        except:
            return "failAuth"
            			        
        return True        

    def connectWithoutPass(self, priv_key_file):
        self.transport = paramiko.SSHClient()
        self.transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.transport.connect(self.host, username=self.user, key_filename=priv_key_file)
        except:
            return "failAuth"
            			        
        return True    

    def exec_command(self,command):
        self.channel = self.transport.get_transport().open_session()
        self.channel.exec_command(command)
        return self.channel
    
    def close(self):
        self.transport.close()
        
    def open_ftp(self):
        self.sftp = self.transport.open_sftp()

    def close_ftp(self):
        self.sftp.close()

    def removeFile(self, _file):
        try:
            self.sftp.remove(_file)
        except:
            pass

    def putFile(self, fileSource, fileDestination):
        try:
            self.sftp.put(fileSource, fileDestination)
        except:
            pass
