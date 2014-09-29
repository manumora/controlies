# coding: utf8
from applications.controlies.modules.Thinclients import Thinclients
from applications.controlies.modules.Groups import Groups
    
def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()
    
@service.json
def getHostData():
    l=conecta()
    h = Thinclients(l,request.vars['name'],"","")
    response = h.getHostData()    
    l.close()
    return dict(response=response)
    
@service.json   
@auth.requires_login()
def list():
    l=conecta()
    h = Thinclients (l,"","","")
    a=request.vars
    response = h.list(a)    
    l.close()
    return response    

@service.json
@auth.requires_login()
def modify():
    l=conecta()
    h = Thinclients(l,request.vars['name'],request.vars['mac'],"")
    response=h.process(request.vars['action'])
    l.close()
    return dict(response=response)
   
@service.json
@auth.requires_login()    
def delete():
    l=conecta()
    h = Thinclients(l,request.vars['host'],"","")
    response=h.process("delete")
    l.close()
    return dict(response=response)

@service.json
@auth.requires_login()
def move():
	
    if request.vars['classroom']=="aula":
        return dict(response="classroom")
    
    if request.vars['computer']=="equipo":
        return dict(response="computer")


    cadena = request.vars['name'].split("-")
    type = cadena[1][:1]

    newName = "a"+request.vars['classroom'].zfill(2)+"-"+type+request.vars['computer'].zfill(2)
  
    l=conecta()
    t1 = Thinclients(l,newName,"","")
    t1.delete()

    t2 = Thinclients(l,request.vars['name'],"","")
    response = t2.move(newName)
    
    l.close()
    return dict(response=response)

@service.json
@auth.requires_login()
def getNodes():
    l=conecta()
    t = Thinclients(l,"","","")
    groups = t.getThinclientGroups()
    return dict(response=sorted(groups["groups"]))

@service.json
@auth.requires_login()
def getComputersNode():
    l=conecta()
    t = Thinclients(l,"","","")
    computers = t.getAllComputersNode(request.vars['node'])
    return dict(response=sorted(computers["computers"]))

@service.json  
@auth.requires_login()    
def getUsers():
    l=conecta()
    g = Groups(l,"",request.vars['name'],"")
    response = g.getGroupUsersData()
    l.close()
    return dict(response=response)  

@service.json
@auth.requires_login()
def saveAssignation():
    l=conecta()
    j=0
    for i in request.vars['computers[]']:
        try:
            t = Thinclients(l,i,"",request.vars['students[]'][j])            
            t.modifyUser();
        except:
            t = Thinclients(l,i,"","")
            t.modifyUser();        
        j=j+1
    return dict(response="OK")

#necesaria estas funciones en el controlador para poder cargar las vistas correspondientes:    

def form():
    return dict()

def form_move():
    return dict()

def assignComputers():
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
