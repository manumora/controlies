# coding: utf8
from applications.controlies.modules.LaptopsTrademarks import LaptopsTrademarks
from applications.controlies.modules.SQLiteConnection import SQLiteConnection
from applications.controlies.modules.Utils import Utils
from applications.controlies.modules.Users import Users

def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()

################## LAPTOPS ####################

@service.json
@auth.requires_login()
def list():    
    l = LaptopsTrademarks(cdb,"","","")
    response = l.list(request.vars)
    return response

@service.json
def getTrademarkData():
    l = LaptopsTrademarks(cdb,request.vars['id_trademark'],"","")
    response = l.getTrademarkData()
    return dict(response=response)

@service.json
@auth.requires_login()    
def modify():
    l = LaptopsTrademarks(cdb,request.vars["id_trademark"],request.vars["trademark"],request.vars["model"])
    response = l.process(request.vars["action"])
    return dict(response = response)            

@service.json
@auth.requires_login()       
def delete():
    l = LaptopsTrademarks(cdb,request.vars["id_trademark"],"","")
    response = l.delete()                         
    return dict(response=response)

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
