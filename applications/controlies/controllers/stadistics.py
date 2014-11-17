# coding: utf8
import applications.controlies.modules.Utils.LdapUtils as LdapUtils
from applications.controlies.modules.Config import Config
from applications.controlies.modules.Users import Users
from applications.controlies.modules.Groups import Groups
from applications.controlies.modules.Hosts import Hosts
from applications.controlies.modules.Thinclients import Thinclients

@service.json   
@auth.requires_login() 
def getInfoLDAP():
    info = {}
    l=conecta()
        
    request.vars["type"]="Profesor"
    request.vars["rows"]="999999999"
    request.vars["page"]="1"
    request.vars["sidx"]="cn"
    request.vars["sord"]="desc"
    

    u = Users(l,"","","","","","","","","")
    response = u.list(request.vars)
    info["teachers"] = response["records"]
        
    request.vars["type"]="Alumno"
    response = u.list(request.vars)
    info["students"] = response["records"]

    g = Groups(l,"","","")
    request.vars["type"]="Aula"        
    response = g.list(request.vars)
    info["course"] = response["records"]

    request.vars["type"]="Departamento"        
    response = g.list(request.vars)
    info["departments"] = response["records"]
    
    h = Hosts (l,"","","","ltsp-server-hosts")
    response = h.list(request.vars)   
    info["ltspservers"] = response["records"]

    h = Hosts (l,"","","","workstation-hosts")
    response = h.list(request.vars)   
    info["workstations"] = response["records"]

    h = Hosts (l,"","","","laptop-hosts")
    response = h.list(request.vars)   
    info["laptops"] = response["records"]

    h = Thinclients (l,"","","","")
    request.vars["cn"]="-o"
    response = h.list(request.vars) 
    info["thinclients"] = response["records"]

    request.vars["cn"]="-p"
    response = h.list(request.vars) 
    info["student-laptops"] = response["records"]

    info["total-computers"] = info["student-laptops"] + info["thinclients"] + info["laptops"] + info["workstations"]
    info["total-users"] = info["teachers"] + info["students"]
    
    l.close()

    return dict(info=info)

@service.json   
@auth.requires_login() 
def index():
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