# coding: utf8
from applications.controlies.modules.Hosts import Hosts
    
def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
    return dict()
    
@service.json
def getHostData():
    l=conecta()
    h = Hosts(l,request.vars['cn'],"","",request.vars['type_host'])
    response = h.getHostData()    
    l.close()
    return dict(response=response)
    
@service.json   
@auth.requires_login()
def list_ltspservers():
    l=conecta()
    h = Hosts (l,"","","","")
    response = h.getLTSPServers()
    l.close()
    return response    
   
   
@service.json   
@auth.requires_login()
def list():
    l=conecta()
    h = Hosts (l,"","","",request.vars['type_host'])
    a=request.vars
    response = h.list(a)    
    l.close()
    return response    

@service.json
@auth.requires_login()
def modify():
    l=conecta()
    ip = "172."+request.vars['subrange']+"."+request.vars['range']+"."+request.vars['ip']    
    h = Hosts(l,request.vars['name'],ip,request.vars['mac'],request.vars['type_host'])
    response=h.process(request.vars['action'])
    l.close()
    return dict(response=response)
   
@service.json
@auth.requires_login()    
def delete():
    l=conecta()
    print request.vars
    if(isinstance(request.vars['cn[]'], str)):
        h = Hosts(l,request.vars['cn[]'],"","",request.vars['type_host'])
        h.process(request.vars['action'])
    else:
        for t in request.vars['cn[]']:
            h = Hosts(l,t,"","",request.vars['type_host'])
            h.process(request.vars['action'])

    l.close()
    return dict(response="OK")

@service.json
@auth.requires_login()    
def getallranges():
    from applications.controlies.modules.Utils import LdapUtils
    l=conecta()
    myRanges = LdapUtils.getAllRanges(l)
    return dict(response=myRanges)
    
#necesaria estas funciones en el controlador para poder cargar las vistas correspondientes:    
def ltspservers():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default',f='index'))
        
    return dict()
    
def workstations():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default',f='index'))
        
    return dict()    

def hardware():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default',f='index'))

    l=conecta()
    search = l.search("ou=Netgroup","cn=hardware-hosts",["cn"])  
    if not search:
        h = Hosts(l,"","","","hardware-hosts")
        h.createStructure()

    return dict()    

def laptops():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default',f='index'))

    l=conecta()
    search = l.search("ou=Netgroup","cn=laptop-hosts",["cn"])  
    if not search:
        h = Hosts(l,"","","","laptop-hosts")
        h.createStructure()

    return dict()    

@service.json
@auth.requires_login()   
def getNetgroups():
    netgroups = ["ltsp-server-hosts","workstation-hosts","laptop-hosts","hardware-hosts"]
    netgroups.remove(request.vars['type_host'])
    return dict(response=netgroups)

@service.json
@auth.requires_login()   
def moveDevice():
    l=conecta()
    hosts = request.vars.hosts.split(",")
    for h in hosts:
        h1 = Hosts(l,h,"","",request.vars['source'])
        h2 = Hosts(l,h,"","",request.vars['netgroup'])
        h1.deleteTriplet()
        h2.addTriplet()

    return dict(response="OK")

def form_ltspserver():
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
