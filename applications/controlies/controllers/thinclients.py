# coding: utf8
from applications.controlies.modules.Thinclients import Thinclients
    
def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()
    
@service.json
def getHostData():
    l=conecta()
    h = Thinclients(l,request.vars['name'],"")
    response = h.getHostData()    
    l.close()
    return dict(response=response)
    
@service.json   
@auth.requires_login()
def list():
    l=conecta()
    h = Thinclients (l,"","")
    a=request.vars
    response = h.list(a)    
    l.close()
    return response    

@service.json
@auth.requires_login()
def modify():
    l=conecta()
    h = Thinclients(l,request.vars['name'],request.vars['mac'])
    response=h.process(request.vars['action'])
    l.close()
    return dict(response=response)
   
@service.json
@auth.requires_login()    
def delete():
    l=conecta()
    h = Thinclients(l,request.vars['host'],"")
    response=h.process("delete")
    l.close()
    return dict(response=response)

@service.json
@auth.requires_login()
def move():
	
    if request.vars['purpose']=="":
        return dict(response="purpose")
	
    l=conecta()
    t1 = Thinclients(l,request.vars['purpose'],"")
    t1.delete()

    t2 = Thinclients(l,request.vars['name'],"")
    response = t2.move(request.vars['purpose'])
    
    l.close()
    return dict(response=response)

#necesaria estas funciones en el controlador para poder cargar las vistas correspondientes:    

def form():
    return dict()

def form_move():
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
