# coding: utf8
from applications.controlies.modules.Hosts import Hosts
from applications.controlies.modules.Users import Users
from applications.controlies.modules.Groups import Groups 
import applications.controlies.modules.Utils.LdapUtils as LdapUtils

def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default',f='index'))
    return dict()

@service.json 
@auth.requires_login()   
def check_groups():
    l=conecta()
    u = Users(l,"","","","","","","","","")
    users = u.getAllUsers()
    
    allUsersUID=[]
    allUsers=[]
    for us in users:
        allUsersUID.append(us['uid'][0])
        allUsers.append("uid="+us['uid'][0]+",ou=People,dc=instituto,dc=extremadura,dc=es")
                    
    g = Groups(l,"","","")
    groups = g.getAllGroups()

    info=[]
    count=1
    for g in groups:
        try:
            if g['groupType'][0]=="school_class" or g['groupType'][0]=="school_department" or g['groupType'][0]=="authority_group":
                for m in g['member']:
                    if m!="" and m not in allUsers:
                        info.append({'id_check':count, 'group':g['cn'][0], 'type':'member', 'user':m, 'info':'dont_exists' })
                        count+=1

                for m in g['memberUid']:
                    if m!="" and m not in allUsersUID:
                        info.append({'id_check':count, 'group':g['cn'][0], 'type':'memberUid', 'user':m, 'info':'dont_exists' })
                        count+=1
        except:
            pass
        
    return dict(info=info)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
