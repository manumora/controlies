##############################################################################
# -*- coding: utf-8 -*-
# Project:      ControlIES
# Module:       LaptopsTrademarks.py
# Purpose:      LaptopsTrademarks class
# Language:     Python 2.5
# Date:         12-Jun-2012.
# Ver:          31-Jun-2012.
# Author:       Manuel Mora Gordillo
# Copyright:    2012 - Manuel Mora Gordillo <manuito @no-spam@ gmail.com>
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

class LaptopsTrademarks(object):

    def __init__(self):
        pass
    
    def __init__(self,DB,id_trademark,trademark,model):
        self.DB = DB
        self.id_trademark = id_trademark        
        self.trademark = trademark
        self.model = model        
        
    def validation(self,action):

        if self.trademark == "":
            return "trademark"

        if self.model == "":
            return "model"
                
        exists = self.existsTrademarkModel(self.trademark,self.model)
        
        if action=="add" and exists!=False:
            return "trademark_model_exists"

        if action=="modify" and exists!=False:
            if exists!=self.id_trademark:
                return "trademark_model_exists"
                
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

        sql = "SELECT * FROM laptops_trademarks WHERE 1=1 "
        
        try:
            if str(args['trademark']) != "None":
                sql = sql+" AND trademark LIKE '%"+str(args['trademark'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['model']) != "None":
                sql = sql+" AND model LIKE '%"+str(args['model'])+"%'"
        except LookupError:
            pass

        sql = sql + " ORDER BY "+args['sidx']+" "+args['sord']+""
        result = self.DB.executesql(sql)

        rows = []
        for reg in result:
            row = {
				"id":reg[0],
				"cell":[reg[1],reg[2]],
				"trademark":reg[1],
				"model":reg[2]
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
        sql = "INSERT INTO laptops_trademarks (id_trademark, trademark, model) "
        sql = sql + "VALUES(null,'"+self.trademark+"','"+self.model+"')"

        result = self.DB.executesql(sql)
        
        return "OK"
            
            
    def modify(self):
        sql = "UPDATE laptops_trademarks SET trademark='"+self.trademark+"', model='"+self.model+"' "
        sql = sql + "WHERE id_trademark='"+str(self.id_trademark)+"'"

        result = self.DB.executesql(sql)
                    
        return "OK"


    def delete(self):
        sql = "DELETE FROM laptops_trademarks WHERE id_trademark='"+str(self.id_trademark)+"'"

        result = self.DB.executesql(sql)
            
        return "OK"


    def existsTrademarkModel(self,trademark,model):
        
        sql = "SELECT id_trademark FROM laptops_trademarks WHERE trademark='"+trademark+"' AND model='"+model+"'"

        result = self.DB.executesql(sql)

        if len(result) > 0:
            return str(result[0][0])
        
        return False
        
    def getTrademarkData(self):
		
        sql="SELECT * FROM laptops_trademarks WHERE id_trademark='"+str(self.id_trademark)+"'"

        result = self.DB.executesql(sql)

        data = {
            "id_trademark":str(result[0][0]),
            "trademark":result[0][1],
            "model":str(result[0][2])
        }
        return data
