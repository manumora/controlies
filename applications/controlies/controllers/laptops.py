# coding: utf8
from applications.controlies.modules.Laptops import Laptops
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from applications.controlies.modules.Utils import Utils
from applications.controlies.modules.Users import Users


def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
        
    return dict()

################## GRID ####################

@auth.requires_login()
def getAllStatesGrid():
    l = LaptopsHistory(cdb,"","","","","","","","")
    r = l.getAllStates()
    
    text=""
    for i in r:
        text+= i["id_state"]+":"+i["state"]+";"
    text = "2:hola"
    return text #{"States":{"Content":text}}

################## LAPTOPS ####################

@service.json
@auth.requires_login()
def list():
    l = Laptops(cdb,"","","","","","","","")
    response = l.list(request.vars)
    return response

@service.json
def getLaptopData():
    l = Laptops(cdb,request.vars['id_laptop'],"","","","","","","")
    response = l.getLaptopData()
    return dict(response=response)

@service.json
def getAllLaptopTypes():
    l = Laptops(cdb,"","","","","","","","")
    response = l.getAllLaptopTypes()
    return dict(response=response)

@service.json
@auth.requires_login()    
def modify():
    serial = request.vars["serial_number"].strip()
    l = Laptops(cdb,request.vars["id_laptop"],
                serial,
                request.vars["name"],
                request.vars["battery_sn"],
                request.vars["charger_sn"],
                request.vars["mac_eth0"],
                request.vars["mac_wlan0"],
                request.vars["id_trademark"])
    response = l.process(request.vars["action"])
        
    return dict(response = response)            

@service.json
@auth.requires_login()       
def delete():
    l = Laptops(cdb,request.vars["id_laptop"],"","","","","","","")
    response = l.delete()                         
    return dict(response=response)

################## LAPTOPS HISTORY ####################

@service.json
@auth.requires_login()
def listHistory():    
    l = LaptopsHistory(cdb,"",request.vars["id_laptop"],"","","","","","")
    response = l.list(request.vars)
    return response

@service.json
@auth.requires_login()    
def modifyHistory():
    l = LaptopsHistory(cdb,request.vars["id_historical"],request.vars["id_laptop"],request.vars["id_state"],request.vars["id_user_type"],request.vars["nif"].strip(),request.vars["username"].strip(),request.vars["name"].strip(),request.vars["comment"])
    response = l.process(request.vars["action"])
    return dict(response = response)   

@service.json
@auth.requires_login()       
def deleteHistory():
    l = LaptopsHistory(cdb,request.vars["id_historical"],"","","","","","","")
    response = l.delete()                         
    return dict(response=response)

@service.json
def getAllStates():
    l = LaptopsHistory(cdb,"","","","","","","","")
    response = l.getAllStates()
    return dict(response=response)

@service.json
def getAllUserTypes():
    l = LaptopsHistory(cdb,"","","","","","","","")
    response = l.getAllUserTypes()
    return dict(response=response)

@service.json
def getDataLDAP():
    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","","")
    response = u.getUserData()
    l.close()
    return dict(response=response)

@service.json
def getDataHistory():
    l = LaptopsHistory(cdb,request.vars["id_historical"],"","","","","","","")
    response = l.getDataHistory()
    return dict(response=response)

@service.json
def getDataLastHistory():
    l = LaptopsHistory(cdb,"",request.vars["id_laptop"],"","","","","","")
    response = l.getLastHistory()
    return dict(response=response)

def laptops():
    return dict()

def history():
    return dict()

def form_history():
    return dict()

def form():
    if not auth.user:
        return "session_out"
    
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
