# coding: utf8
from applications.controlies.modules.Groups import Groups
from applications.controlies.modules.Users import Users
from applications.controlies.modules.Laptops import Laptops
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from applications.controlies.modules.SQLiteConnection import SQLiteConnection

def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()

@service.json
@auth.requires_login()
def list():
    l=conecta()
    g = Groups(l,"school_class","","")
    a=request.vars
    response = g.list(a)
    l.close()

    return response  

@service.json  
@auth.requires_login()    
def getUsers():
    l=conecta()
    g = Groups(l,"",request.vars['row_id'],"")
    response = g.listUsers(request.vars)
    l.close()

    # Obtenemos los numeros de serie de los portatiles
    sql = "SELECT lh.username, l.serial_number, lt.trademark, lt.model FROM laptops l" 
    sql = sql+" LEFT JOIN laptops_historical lh ON l.id_laptop=lh.id_laptop"
    sql = sql+" LEFT JOIN laptops_trademarks lt ON l.id_trademark=lt.id_trademark" 
    sql = sql+" GROUP BY l.id_laptop ORDER BY lh.datetime desc"
    result = cdb.executesql(sql)

    serials={}
    for r in result:
        if str(r[0])!="":
            serials[str(r[0])]={'serial':str(r[1]), 'trademark':str(r[2])+' - '+str(r[3])}

    rows=[]
    for r in response["rows"]:
        num=""
        trademark=""
        if r["cell"][1] in serials:
            num = serials[r["cell"][1]]['serial']
            trademark = serials[r["cell"][1]]['trademark']

        r["cell"].append(num)
        r["serial_number"]=num
        r["cell"].append(trademark)
        r["trademark"]=trademark
        rows.append(r)

    response["rows"]=rows
    return response  

@service.json
@auth.requires_login()
def modifySerialNumber():
    serialNumber = request.vars["serial_number"].strip()
    
    if serialNumber=="":
        response = "unassignment"
    else:
        l = Laptops(cdb,"","","","","","","","")
        id_laptop = l.existsSerialNumber(serialNumber)
        response=""
        if not id_laptop:
            response = "not_exists"
        else:
            lh = LaptopsHistory(cdb,"",id_laptop,"","","","","","")
            data = lh.getLastHistory()
            if data["username"]!="" and data["username"]!=request.vars['id']:
                response = "already_assigned"
            elif data["username"]!="" and data["username"]==request.vars['id']:
                response = "OK"
            else:
                userData = getUserData(request.vars["id"])
    
                lh = LaptopsHistory(cdb,"",id_laptop,"2","2",userData["nif"],request.vars["id"],userData["name"],"Reasignado")
                lh.add()
                response="OK"

    return dict(response=response)

@service.json
@auth.requires_login()
def reassignmentSerialNumber():
    serialNumber = request.vars["serial_number"].strip()
    newSerialNumber = request.vars["newSerial"].strip()
    
    l = Laptops(cdb,"","","","","","","","")
            
    if serialNumber!="":
        id_laptop = l.existsSerialNumber(serialNumber)
        unassignmentLaptop(id_laptop)
    
    if newSerialNumber!="":
        userData = getUserData(request.vars["username"])
    
        id_laptop = l.existsSerialNumber(newSerialNumber)
        lh = LaptopsHistory(cdb,"",id_laptop,"2","2",userData["nif"],request.vars["username"],userData["name"],"Reasignado")
        lh.add()

    return dict(response="OK") 

@service.json
@auth.requires_login()    
def addLaptop():
    serialNumber = request.vars["serial_number"].strip()
    l = Laptops(cdb,"",
                serialNumber,
                request.vars["name"],
                request.vars["battery_sn"],
                request.vars["charger_sn"],
                request.vars["mac_eth0"],
                request.vars["mac_wlan0"],
                request.vars["id_trademark"])
    response = l.process("add")
    
    if response=="OK":
        userData = getUserData(request.vars["username"])

        max = l.getMaxId()
        lh = LaptopsHistory(cdb,"",max,"2","2",userData["nif"],request.vars["username"],userData["name"],"")
        
        id_laptop = lh.userAssignment()
        if id_laptop:
            unassignmentLaptop(id_laptop)
             
        lh.add()
    
    return dict(response = response)  

def getUserData(username):
    ld=conecta()
    u = Users(ld,"","","","",username,"","","","")
    userData = u.getUserData() 
    ld.close()
    return userData

def unassignmentLaptop(id_laptop):
    unassignment = LaptopsHistory(cdb,"",id_laptop,"1","","","","","Desasignado")
    unassignment.add()
    
def search():
    return dict()

def form():
    return dict()
    
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
