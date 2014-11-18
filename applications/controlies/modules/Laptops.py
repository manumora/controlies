##############################################################################
# -*- coding: utf-8 -*-
# Project:      ControlIES
# Module:       Laptops.py
# Purpose:      Laptops class
# Language:     Python 2.5
# Date:         31-May-2012.
# Ver:          31-May-2012.
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
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from Utils import ValidationUtils

class Laptops(object):

    def __init__(self):
        pass
    
    def __init__(self,DB,id_laptop,serial_number,name,battery_sn,charger_sn,mac_eth0,mac_wlan0,id_trademark):
        self.DB = DB
        self.id_laptop = id_laptop        
        self.serial_number = serial_number
        self.name = name
        self.battery_sn = battery_sn
        self.charger_sn = charger_sn
        self.mac_eth0 = mac_eth0
        self.mac_wlan0 = mac_wlan0
        self.id_trademark = id_trademark        
        
    def validation(self,action):

        if self.id_trademark == "none":
            return "id_trademark"

        if self.serial_number == "":
            return "serial_number"
        
        exists = self.existsSerialNumber(self.serial_number)
        
        if action=="add" and exists!=False:
            return "serial_number_exists"

        if action=="modify" and exists!=False:
            if exists!=self.id_laptop:
                return "serial_number_exists"
            
        # Validacion mac eth0
        if self.mac_eth0 != "":
            if not ValidationUtils.validMAC(self.mac_eth0):
                return "mac_eth0"
            
            existsMAC_eth0 = self.existsMAC(self.mac_eth0)
    
            if action=="add" and existsMAC_eth0!=False:
                return "mac_eth0_exists"
    
            if action=="modify" and existsMAC_eth0!=False:
                if existsMAC_eth0!=self.id_laptop:
                    return "mac_eth0_exists"

        # Validacion mac wlan0
        if self.mac_wlan0 != "":
            if not ValidationUtils.validMAC(self.mac_wlan0):
                return "mac_wlan0"
    
            existsMAC_wlan0 = self.existsMAC(self.mac_wlan0)
            
            if action=="add" and existsMAC_wlan0!=False:
                return "mac_wlan0_exists"
    
            if action=="modify" and existsMAC_wlan0!=False:
                if existsMAC_wlan0!=self.id_laptop:
                    return "mac_wlan0_exists"

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

        sql = "SELECT l.id_laptop, lt.trademark, lt.model, l.serial_number, ut.user_type, lh.username, lh.datetime, s.state"
        sql = sql+" FROM laptops l, laptops_historical lh"
        sql = sql+" LEFT JOIN laptops_trademarks lt ON l.id_trademark=lt.id_trademark "        
        #sql = sql+" INNER JOIN laptops_historical lh ON l.id_laptop=lh.id_laptop"
        sql = sql+" LEFT JOIN states s ON lh.id_state=s.id_state "
        sql = sql+" LEFT JOIN users_types ut ON ut.id_user_type=lh.id_user_type "     
        sql = sql+" WHERE 1=1 "
        sql = sql+" AND l.id_laptop=lh.id_laptop "

        if str(args['typeSearch']) == "current":
            sql = sql+" AND lh.id_historical IN (SELECT MAX(lh2.id_historical) FROM laptops_historical lh2 WHERE lh2.id_laptop=l.id_laptop) "
                
        try:
            if str(args['serial_number']) != "None":
                sql = sql+" AND l.serial_number LIKE '%"+str(args['serial_number'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['trademark']) != "None":
                sql = sql+" AND lt.trademark LIKE '%"+str(args['trademark'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['model']) != "None":
                sql = sql+" AND lt.model LIKE '%"+str(args['model'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['user_type']) != "None":
                if str(args['user_type']) == "Ninguno":
                    sql = sql+" AND (lh.id_user_type='' OR lh.id_user_type='0')"
                else:
                    sql = sql+" AND ut.user_type='"+str(args['user_type'])+"'"
        except LookupError:
            pass

        try:
            if str(args['username']) != "None":
                sql = sql+" AND lh.username LIKE '%"+str(args['username'])+"%'"
        except LookupError:
            pass

        try:
            if str(args['state']) != "None":
                sql = sql+" AND s.state LIKE '%"+str(args['state'])+"%'"
        except LookupError:
            pass

        if str(args['typeSearch']) == "current":
            sql = sql + " GROUP BY l.id_laptop"
            
        sql = sql + " ORDER BY "+args['sidx']+" "+args['sord']+", lh.datetime desc"
        result = self.DB.executesql(sql)

        rows = []
        for reg in result:
            row = {
				"id":reg[0],
				"cell":[reg[1],reg[2],reg[3],reg[4],reg[5],reg[6],reg[7]],
				"trademark":reg[1],
				"model":reg[2],
				"serial_number":reg[3],
                "user_type":reg[4],
                "username":reg[5],
                "datetime":reg[6],
                "state":reg[7],
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

        sql = "INSERT INTO laptops (id_laptop,serial_number,name,battery_sn,charger_sn,mac_eth0,mac_wlan0,id_trademark)"
        sql = sql+" VALUES (null,'"+self.serial_number+"','"+self.name+"','"+self.battery_sn+"','"+self.charger_sn+"','"+self.mac_eth0+"','"+self.mac_wlan0+"',"+self.id_trademark+")"  
        result = self.DB.executesql(sql)
        self.id_laptop = self.getMaxId()

        lh = LaptopsHistory(self.DB,"",self.id_laptop,"1","0","","","","Nuevo en el sistema","")
        lh.add()

        return "OK"
            
            
    def modify(self):
        self.DB(self.DB.laptops.id_laptop==self.id_laptop).update(serial_number=self.serial_number,
                                                                  name=self.name,
                                                                  battery_sn=self.battery_sn,
                                                                  charger_sn=self.charger_sn,
                                                                  mac_eth0=self.mac_eth0,
                                                                  mac_wlan0=self.mac_wlan0,
                                                                  id_trademark=self.id_trademark)
        self.DB.commit()
        return "OK"


    def delete(self):
        self.DB(self.DB.laptops.id_laptop==self.id_laptop).delete()
        self.DB(self.DB.laptops_historical.id_laptop==self.id_laptop).delete()
        self.DB.commit()
        return "OK"


    def existsSerialNumber(self,serial_number):
        
        sql = "SELECT p.id_laptop FROM laptops p WHERE p.serial_number='"+serial_number+"'"
        result = self.DB.executesql(sql)

        if len(result) > 0:
            return str(result[0][0])
        
        return False

    def existsMAC(self,mac):
        
        sql = "SELECT p.id_laptop FROM laptops p WHERE p.mac_eth0='"+mac+"' OR p.mac_wlan0='"+mac+"'"
        result = self.DB.executesql(sql)

        if len(result) > 0:
            return str(result[0][0])
        
        return False

    def getLaptopData(self):
		
        sql="SELECT l.id_laptop, l.serial_number, l.id_trademark, lt.trademark, lt.model, l.name, l.battery_sn, l.charger_sn, mac_eth0, mac_wlan0 "
        sql=sql+" FROM laptops l"
        sql=sql+" LEFT JOIN laptops_trademarks lt  ON l.id_trademark=lt.id_trademark"
        sql=sql+" WHERE l.id_laptop='"+str(self.id_laptop)+"'"
        result = self.DB.executesql(sql)
        
        try:
            trademark = str(result[0][3]+"/"+result[0][4])
        except:
            trademark = ""
            
        dataLaptop = {
            "id_laptop":str(result[0][0]),
            "serial_number":result[0][1],
            "id_trademark":str(result[0][2]),
            "trademark":trademark,
            "name":str(result[0][5]),
            "battery_sn":str(result[0][6]),
            "charger_sn":str(result[0][7]),
            "mac_eth0":str(result[0][8]),
            "mac_wlan0":str(result[0][9]),
        }
        return dataLaptop

    def getAllLaptopTypes(self):
        sql="SELECT id_trademark, trademark, model FROM laptops_trademarks ORDER BY trademark"
        result = self.DB.executesql(sql)

        data=[]
        for r in result:
            dataType = {
                "id_trademark":str(r[0]),
                "trademark":r[1]+" / "+r[2]
            }
            data.append(dataType)
        return data

    def getMaxId(self):
        sql="SELECT max(id_laptop) AS max FROM laptops"
        result = self.DB.executesql(sql)

        return str(result[0][0])
    
    def getIdbySerialNumber (self, serial_number):
        sql="SELECT id_laptop FROM laptops WHERE serial_number = '" + serial_number + "'"
        result = self.DB.executesql(sql)
        
        return str(result[0][0])
    
    def getIdLaptop(self):
        return self.id_laptop    