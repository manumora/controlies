##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    LdapConnection.py
# Purpose:     Connection with ldap server
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

import ldap
import logging


ldap_secure=True
ldap_cert='/etc/ldap/ssl/ldap-server-pubkey.pem'
ldapmode='uid'
   
    
class LdapConnection(object):
    
    def __init__(self,session):
        self.host = session.server
        self.user = session.username
        self.passwd = session.password

    def setCredentials(self,host,user,passwd):
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
        self.connection=ldap.open(self.host)
        try:
            self.connection.simple_bind_s("cn="+self.user+",ou=People,dc=instituto,dc=extremadura,dc=es",self.passwd)
        except ldap.INVALID_CREDENTIALS:
            logging.getLogger().debug('LDAP user or password incorrect')
            return False
        except ldap.CONFIDENTIALITY_REQUIRED:
            try:
                #self.connection.set_option(ldap.OPT_X_TLS_DEMAND, True)
                self.connection=ldap.initialize("ldaps://" +self.host)
                self.connection.simple_bind_s("cn="+self.user+",ou=People,dc=instituto,dc=extremadura,dc=es",self.passwd)
                return True
            except ldap.LDAPError,e:
                logging.getLogger().debug('A secure connection with the ldap server could not be established')
                return False          
                
        except ldap.LDAPError,e:
            logging.getLogger().debug('LDAP error %s' % e.message["desc"])
            return False

        return True

    def getConnect(self):
        return self.connection
        
    def search(self,baseDN,filter,retrieveAttributes):
        
        try:
            ldap_result_id = self.connection.search(baseDN+",dc=instituto,dc=extremadura,dc=es", ldap.SCOPE_SUBTREE, filter, retrieveAttributes)
            result_set = []
            while 1:
                result_type, result_data = self.connection.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            return result_set
        except ldap.LDAPError, e:
            logging.getLogger().debug('LDAP error search')
        
        """result = con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs )
        return result"""

    def searchOneLevel(self,baseDN,filter,retrieveAttributes):
        
        try:
            ldap_result_id = self.connection.search(baseDN+",dc=instituto,dc=extremadura,dc=es", ldap.SCOPE_ONELEVEL, filter, retrieveAttributes)
            result_set = []
            while 1:
                result_type, result_data = self.connection.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            return result_set
        except ldap.LDAPError, e:
            logging.getLogger().debug('LDAP error search')
        
        """result = con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs )
        return result"""

    def add(self,baseDN,attr):
        try:
            self.connection.add_s(baseDN+",dc=instituto,dc=extremadura,dc=es", attr)
            
        except ldap.ALREADY_EXISTS:
            logging.getLogger().debug("LDAP already exists %s" % (baseDN))
        except ldap.OPERATIONS_ERROR:
            logging.getLogger().debug("LDAP operation error %s" % (baseDN))
        except ldap.NO_SUCH_OBJECT:
            logging.getLogger().debug("LDAP no such object %s" % (baseDN))
            
        return True

    def modify(self,baseDN,attr):
        try:
            self.connection.modify_s(baseDN+",dc=instituto,dc=extremadura,dc=es", attr)
            
        except ldap.OPERATIONS_ERROR:
            print "error"
        except ldap.NO_SUCH_OBJECT:
            print "no_such_object"
        except Exception,e:
            print e
            
        return True
        
    def delete(self,baseDN):
        try:
            self.connection.delete_s(baseDN+",dc=instituto,dc=extremadura,dc=es")
            
        except ldap.OPERATIONS_ERROR:
            print "error"
        except ldap.NO_SUCH_OBJECT:
            print "no_such_object"
            
        return True
        
        
    def close(self):
        self.connection.unbind()
        

