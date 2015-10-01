# coding: utf8
from applications.controlies.modules.Groups import Groups
                
def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()

@service.json
@auth.requires_login()
def list():
    l=conecta()
    
    # Corrige grupos con miembros vacios
    """import applications.controlies.modules.Utils.LdapUtils as LdapUtils
    response = LdapUtils.getClassroomGroupsWithUsers(l)
    for i in response["classrooms"]:
        list2 = [x for x in i[i.keys()[0]] if x]
        if len(list2)>0:
            users = ",".join(list2)
            g = Groups(l,"school_class", i.keys()[0], users)
            g.process("modify")    
    """    
    #return response
    
    
    g = Groups(l,"","","")
    a=request.vars
    response = g.list(a)
    l.close()
    return response  
    
@service.json 
def getAllGroups():
    import applications.controlies.modules.Utils.LdapUtils as LdapUtils
    l=conecta()
    response = LdapUtils.getAllGroups(l)
    l.close()
    return response
    
@service.json
@auth.requires_login()
def modify():
    l=conecta()
    g = Groups(l,request.vars['type'], request.vars['name'], request.vars['users'])
    response = g.process(request.vars['action'])    
    l.close()
    return dict(response=response)
    

@service.json  
def getGroupData():
    l=conecta()
    g = Groups(l,"",request.vars['name'],"")
    response = g.getGroupData()
    l.close()
    return dict(response=response)

@service.json  
@auth.requires_login()    
def delete():
    l=conecta()
    g = Groups(l,"",request.vars['name'],"")
    response = g.delete()
    l.close()
    return dict(response=response)

@service.json  
@auth.requires_login()    
def getUsers():
    l=conecta()
    g = Groups(l,"",request.vars['row_id'],"")
    response = g.listUsers(request.vars)
    l.close()
    return response  
    
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
