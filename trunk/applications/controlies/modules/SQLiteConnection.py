##############################################################################
# -*- coding: utf-8 -*-
# Project:     ControlIES
# Module:    SQLiteConnection.py
# Purpose:     Connection with sqlite
# Language:    Python 2.5
# Date:        23-May-2012.
# Ver:        23-May-2012.
# Authores:    Manuel Mora Gordillo
#				Francisco Damian Mendez Palma
# Copyright:    2012 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#				2012 - Francisco Damian Mendez Palma <fmendezpalma @no-spam@ gmail.com>
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

from gluon.sql import *

class SQLiteConnection(object):
    
    def __init__(self):
        self.db = DAL('sqlite://controlies.sqlite')
        
    def define_tables(self):
        self.db.define_table('laptops', 
                        Field('id_laptop','integer'),
                        Field('serial_number','string'),
                        Field('id_trademark','integer'),
                        primarykey=['id_laptop'])

        self.db.define_table('laptops_trademarks', 
                        Field('id_trademark','integer'),
                        Field('trademark','string'),
                        Field('model','string'),
                        primarykey=['id_trademark'])

        self.db.define_table('users_types', 
                        Field('id_user_type','integer'),
                        Field('user_type','string'),
                        primarykey=['id_user_type'])

        try:
            self.db.users_types.insert(id_user_type='1',user_type='Profesor')
        except:
            pass

        try:
            self.db.users_types.insert(id_user_type='2',user_type='Alumno')
        except:
            pass

        self.db.define_table('laptops_historical', 
                        Field('id_historical','integer'),
                        Field('id_laptop','integer'),                        
                        Field('datetime','datetime'),
                        Field('username','string'),
                        Field('name','string'),
                        Field('id_user_type','integer'),
                        Field('nif','string'),
                        Field('comment','string'),
                        Field('id_state','integer'),
                        primarykey=['id_historical'])

        self.db.define_table('states', 
                        Field('id_state','integer'),
                        Field('state','string'),                        
                        primarykey=['id_state'])
        try:
            self.db.states.insert(id_state='1',state='Sin asignar')
        except:
            pass

        try:
            self.db.states.insert(id_state='2',state='Asignado')
        except:
            pass

        try:
            self.db.states.insert(id_state='3',state='En reparación')
        except:
            pass

    def getDB(self):
        return self.db