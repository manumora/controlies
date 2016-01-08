# -*- coding: utf-8 -*-

from applications.controlies.modules.Utils import Utils

@auth.requires_login()
def index():

    try:
        dir_ssh = "/var/web2py/applications/controlies"
        #dir_ssh = "/home/manu/proyectos/controlies/applications/controlies"
        if not os.path.isfile(dir_ssh+"/.ssh/id_rsa.pub"):
            Utils.generateRSAkeys(dir_ssh)
    except:
        pass
    
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    if "host" in request.vars:
        session.server=request.vars["host"]
        session.username=request.vars["username"]        
        session.password=request.vars["password"]
        con_parameters=auth.settings.login_methods[0].func_defaults

        """session.secureAuth = "off"
        if request.vars["secureAuth"]=="on":
            session.secureAuth= request.vars["secureAuth"]"""

        if con_parameters[0] != request.vars["host"] or request.vars["username"] != 'admin':
            #tengo que cambiar los parámetros con los que se llama a la función de logueo:
            new_parameters=list(con_parameters)
            new_parameters[0]=request.vars["host"]
            #if request.vars["username"] != 'admin' : new_parameters[3]='uid'
            #auth.settings.login_methods[0].func_defaults=tuple(new_parameters)


    return dict(form=auth())

@auth.requires_login()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)

def login_status():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        return 'location.href = "%s"' % URL('default', 'index')
    else:
        return ''

@auth.requires_login()
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
