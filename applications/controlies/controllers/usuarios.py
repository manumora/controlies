# coding: utf8
from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils
    
def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()


@service.json
@auth.requires_login()
def list():
    l=conecta()
    u = Users(l,"","","","","","","","","")
    response = u.list(request.vars)
    l.close()
    return response    

@service.json
@auth.requires_login()    
def searchUsername():
    l=conecta()
    u = Users(l,"",request.vars['name'],request.vars['name'],"","","","","","")
    response = u.searchNewUsername() 
    l.close()                
    return dict(response=response)
    
@service.json
def getUserData():
    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","")
    response = u.getUserData()
    l.close()
    return dict(response=response)


@service.json      
def getAllUsers():
    import applications.controlies.modules.Utils.LdapUtils as LdapUtils
    l=conecta()
    response = LdapUtils.getAllUsers(l)
    l.close()
    return response

@service.json
@auth.requires_login()       
def delete():
    l=conecta()

    if(isinstance(request.vars['user[]'], str)):        
        u = Users(l,"","","","",request.vars['user[]'],"","","","")
        u.delete()  
    else:
        for h in request.vars['user[]']:
            u = Users(l,"","","","",h,"","","","")
            u.delete()

    l.close()                          
    return dict(response="OK")

@service.json
@auth.requires_login()    
def modify_user():

    l=conecta() 
    departments=[]
    classrooms=[]                
    if 'multiselect_departments' in request.vars: departments = request.vars['multiselect_departments']
    if 'multiselect_classrooms' in request.vars:classrooms = request.vars['multiselect_classrooms']

    u = Users(l,request.vars['type'],request.vars['name'],request.vars['surname'],request.vars['nif'],request.vars['user'],request.vars['password'],request.vars['password2'],departments,classrooms)
    response = u.process(request.vars['action'])
    l.close()
    return dict(response = response)    
    #return dict(response = "OK")        

@service.json
@auth.requires_login()   
def create_home_directory_withoutpass():
    from applications.controlies.modules.SSHConnection import SSHConnection

    c = SSHConnection("servidor","root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")

    if response != True:
		return dict(response = response)
		
    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","")
    responseUser = u.getUserData()
    l.close()

    homeDirectory = Utils.homeDirectory(request.vars['type'])+responseUser["user"]
			
    c.exec_command("cp -r /etc/skel "+homeDirectory)
    c.exec_command("chown -R "+responseUser["uidnumber"]+":"+responseUser["gidnumber"]+" "+homeDirectory)
    c.close()

    return dict(response = "OK")


@service.json
@auth.requires_login()   
def create_home_directory():
    from applications.controlies.modules.SSHConnection import SSHConnection

    #c = SSHConnection(request.vars['host'],request.vars['user'],request.vars['password'])
    c = SSHConnection("servidor","root",request.vars['password'])
    response = c.process()
    print request.vars
    if response != True:
		return dict(response = response)

    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","")
    responseUser = u.getUserData()
    l.close()

    homeDirectory = Utils.homeDirectory(request.vars['type'])+responseUser["user"]
			
    c.exec_command("cp -r /etc/skel "+homeDirectory)
    c.exec_command("chown -R "+responseUser["uidnumber"]+":"+responseUser["gidnumber"]+" "+homeDirectory)

    try:
		if request.vars["trustRelationship"] == "on":
			dir_ssh = "/var/web2py/applications/controlies"
			Utils.generateRSAkeys(dir_ssh)
			c.open_ftp()
			c.removeFile("/tmp/controlIES_rsa.pub")
			c.putFile(dir_ssh+"/.ssh/id_rsa.pub","/tmp/controlIES_rsa.pub")
			c.exec_command('cat /tmp/controlIES_rsa.pub >> /root/.ssh/authorized_keys')
			c.close_ftp()
    except:
		pass

    c.close()    
    return dict(response = "OK")       
    
def form():
    return dict()

def form_home_directory():
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
