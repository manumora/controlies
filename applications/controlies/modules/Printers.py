##############################################################################
# -*- coding: utf-8 -*-
# Project:      ControlIES
# Module:       Laptops.py
# Purpose:      Laptops class
# Language:     Python 2.5
# Date:         31-May-2012.
# Ver:          31-May-2012.
# Author:       Manuel Mora Gordillo
#               Francisco Méndez Palma
# Copyright:    2012 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
#               2012 - Francisco Méndez Palma <fmendezpalma @no-spam@ gmail.com>
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

from math import floor
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from Utils import ValidationUtils

class Printers(object):

    def __init__(self):
        pass
    
    def __init__(self,DB,id_printer,id_printer_trademark,model,location):
        self.DB = DB
        self.id_printer = id_printer        
        self.id_printer_trademark = id_printer_trademark
        self.model = model
        self.location = location
        
    def validation(self,action):

        if self.id_printer_trademark == "none":
            return "id_printer_trademark"

        if self.model == "":
            return "model"
        
        if self.location == "":
            return "location"        
        

        return "OK"

    def process(self,action):
        if action == "add":
            val = self.validation(action)
            
            if val != "OK":
                return val
            else:
                response = self.add()
                return response

        if action == "modify":
            val = self.validation(action)
            
            if val != "OK":
                return val
            else:
                response = self.modify()
                return response
        
            
    def list(self,args):

        sql = "SELECT p.id_printer, pt.trademark, p.model"
        sql = sql+" FROM printers p, printers_trademarks pt"
        sql = sql+" WHERE p.id_printer_trademark = pt.id_printers_trademark "


        try:
            if str(args['model']) != "None":
                sql = sql+" AND p.model LIKE '%"+str(args['model'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['trademark']) != "None":
                sql = sql+" AND pt.trademark LIKE '%"+str(args['trademark'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['location']) != "None":
                sql = sql+" AND p.location LIKE '%"+str(args['location'])+"%'"
        except LookupError:
            pass

        sql = sql + " GROUP BY p.id_printer"
        sql = sql + " ORDER BY "+args['sidx']+" "+args['sord']

        result = self.DB.executesql(sql)

        rows = []
        for reg in result:
            row = {
                "id":reg[0],
                "cell":[reg[1],reg[2]],
                "trademark":reg[1],
                "model":reg[2],
            }
            rows.append(row)

        # grid parameters
        limit = int(args['rows'])
        page = int(args['page'])
        start = limit * page - limit
        finish = start + limit;             
                    
        # grid parameters
        if len(rows) > 0:
            totalPages = floor( len(rows) / int(limit) )
            module = len(rows) % int(limit)

            if module > 0:
                totalPages = totalPages+1
        else:
            totalPages = 0

        if page > totalPages:
            page = totalPages

        return { "page":page, "total":totalPages, "records":len(rows), "rows":rows[start:finish] }


    def add(self):
        #self.DB.laptops.insert(serial_number=self.serial_number,id_trademark=int(self.id_trademark))
        #self.DB.commit()

        sql = "INSERT INTO printers (id_printer,id_printer_trademark,model,location)"
        sql = sql+" VALUES (null,"+self.id_printer_trademark+",'"+self.model+"','"+self.location+"')"
        result = self.DB.executesql(sql)

        return "OK"
            
            
    def modify(self):
        self.DB(self.DB.printers.id_printer==self.id_printer).update(id_printer_trademark=self.id_printer_trademark,
                                                                  model=self.model,
                                                                  location=self.location)
        self.DB.commit()
        return "OK"


    def delete(self):
        self.DB(self.DB.printers.id_printer==self.id_printer).delete()
        self.DB.commit()
        return "OK"

