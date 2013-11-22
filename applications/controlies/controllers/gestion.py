# coding: utf8
from applications.controlies.modules.Hosts import Hosts
from applications.controlies.modules.Rayuela2Ldap import Rayuela  
import applications.controlies.modules.Utils.LdapUtils as LdapUtils
from applications.controlies.modules.SQLiteConnection import SQLiteConnection
from applications.controlies.modules.Laptops import Laptops
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from applications.controlies.modules.Config import Config

import xmlrpclib
import gluon.contrib.simplejson
from gluon.tools import Mail

@service.json   
@auth.requires_login()
def base_datos():
    import StringIO
    import os

    right_version=right_firefox_version(request.env.http_user_agent)

    if not "archivos" in session.keys():
        session.archivos=[]    
   
    form=SQLFORM.factory(submit_button='Enviar')
    if form.accepts(request.vars, session):
        response.flash = 'Procesando datos, espere'
        #borrando = form.vars.principiocurso
        if len(session.archivos)>0:
            import pdb
            lista_completa=[]                           
            #SQLite=SQLiteConnection()
            #SQLite.define_tables()
            
            #dbcontrolies = SQLite.getDB()
            #result = db.executesql(sql)
            for archivo in session.archivos:
                f = open(archivo)
                linea = f.readline()
                last_id = ""
                while linea:
                    if linea!= '\n' and linea != '':
                        linea = linea.split(",")
                        # Datos del portatil
                  
                        serial_number = linea[1].replace("'","")
                        id_trademark = linea[2]
                        laptop = Laptops (cdb,"",serial_number, id_trademark)
                                                
                        if not laptop.existsSerialNumber (laptop.serial_number):
                            laptop.add ()
                            last_id = laptop.getIdbySerialNumber (laptop.serial_number)
                                
                        if last_id:
                            # Datos del registro historico
                            id_laptop = last_id
                            username = linea [9].replace("'","")
                            name = linea [10].replace("'","")
                            id_user_type = linea [6]
                            nif = linea [5].replace("'","")
                            id_state = linea [8]
                                
                            laptopshistory = LaptopsHistory (cdb, "", id_laptop, id_state, id_user_type, nif, username, name, "")
                            laptopshistory.add ()
                            #dbcontrolies.laptops_historical.insert (**attributes)
                                
                    linea = f.readline()

            response.flash = T('Ficheros importados correctamente')        
            session.archivos=[]
        
    return dict(form=form,right_version=right_version)
    
@service.json   
@auth.requires_login()
def servidores_aula():
    if not auth.user: redirect(URL(c='default',f='index'))
    return dict()
    
@service.json   
@auth.requires_login()    
def getClassroomDetails():
    import xmlrpclib
    from applications.controlies.modules.Users import Users
    l=conecta()
    objUser = Users(l,"","","","",request.vars['teacher'],"","","","")
    teacherData = objUser.getUserData()

    s = xmlrpclib.Server("http://" + request.vars['classroom'] + ":8900");

    users = s.Users()

    response = []
    for u in users:
        user = u.split("@")

        objUser = Users(l,"","","","",user[0],"","","","")
        photo = objUser.getUserPhoto()

    #    response.append({ 'username': user[0], 'host': user[1], 'photo': photo })

    #return json.dumps({ "teacher" : teacherData, "classroom" : request.args['classroom'][0], "students" : response })



    return dict()
  


@auth.requires_login()    
def rayuela():
    if not auth.user: redirect(URL(c='default',f='index'))
    
    import StringIO

    right_version=right_firefox_version(request.env.http_user_agent)

    if not "archivos" in session.keys():
        session.archivos=[]    
    form=SQLFORM.factory(Field('principiocurso','boolean',default=False ),submit_button='Enviar')
    if form.accepts(request.vars, session):
        response.flash = 'Procesando datos, espere'
        borrando = form.vars.principiocurso
        if len(session.archivos)>0:
            l=conecta()
            usuarios=[]

            try:
                os.mkdir( "/tmp/rayuela-ldap")
            except:
                pass #problema de permisos o directorio ya creado 

            lista_completa=[]                           
            for archivo in session.archivos:
                rayuela=Rayuela(l,archivo,borrando)
                todos=rayuela.gestiona_archivo()
                lista_completa +=[(archivo,)]
                lista_completa +=todos
                lista_completa +=[("--",)]
                
            session.archivos=[]    
            #LdapUtils.sanea_grupos(l)                               
            l.close()
            
            #generamos el archivo de salida 
            s=StringIO.StringIO()

            for entrada in lista_completa:
                if len(entrada)<3:
                    s.write(entrada[0]+ '\n' + '\n')
                else:
                    linea=entrada[0] + " - "
                    if entrada[1]:
                        linea +=entrada[2]
                        linea +='\n'
                    else:
                        linea += "USUARIO ANTIGUO\n"
                    s.write(linea)             
                          
            response.headers['Content-Type']='text/txt'
            response.headers['Content-Disposition'] = 'attachment;filename=usuarios.txt'
            return s.getvalue()


        session.archivos=[]
  
    
    return dict(form=form,right_version=right_version)



@auth.requires_login()  
def subida_rayuela():

###################################################
#
# Used for file upload (with multiple file up) + Need rework (too much queries
#
###################################################

    if "archivos" not in session.keys():archivos=[]
  
    for r in request.vars:
        if r=="qqfile" or r=="userfile":
            try:
                size = 0
                #
                # Differ between web2py server and apache
                #
                if request.env.has_key('http_content_length'):
                    size = int(request.env['http_content_length'])
                else:
                    size = int(request.env['content_length'])
                logger.debug(size)
            except:
                raise HTTP(405,'not enough space')            
                
           
            parentpath="/tmp/"
            if r=="qqfile":
                file=request.vars.qqfile
            else:
                file=request.vars.userfile.filename
            logger.debug('New file uploading : ' + file)
            #
            # Re-arange file
            #
            filename=file.replace(' ','_')
            filepath=parentpath+filename
            f = open(filepath, 'wb')
            if r=="qqfile":
                data=request.body.read()
            else:
                data=request.vars.userfile.file.read()
                
            f.write(data)
            f.close()
           
            session.archivos.append(filepath)
            
            print session.archivos
            return response.json({'success':'true'})
            # else:
            #     return response.json({'success':'false'})
    return response.json({'success':'false'})



@service.json   
@auth.requires_login()    
def getLTSPServers():
    l=conecta()
    h = Hosts (l,"","","","ltsp-server-hosts")
    #h = Hosts (l,"","","","workstation-hosts")    
    response = h.getListTriplets()
    l.close()
    return dict(response=response)


@service.json   
@auth.requires_login()    
def getWorkstations():
    l=conecta()
    h = Hosts (l,"","","","workstation-hosts")    
    response = h.getListTriplets()
    l.close()
    return dict(response=response)


@service.json   
@auth.requires_login()    
def getLaptops():
    l=conecta()
    h = Hosts (l,"","","","laptop-hosts")    
    response = h.getListTriplets()
    l.close()
    return dict(response=response)


@service.json   
@auth.requires_login()    
def getLTSPStatus():

    """import memcache
    shared = memcache.Client(['127.0.0.1:11211'], debug=0)    
    fileNameServers = shared.get('fileNameServers')
    fileNameTeachers = shared.get('fileNameTeachers')"""

    directory = "/tmp/"
    fileNameServers = directory+"controliesSerFDidisDSs43"
    fileNameTeachers = directory+"controliesTeaRssdASWe234"

    try:
        f = open(fileNameServers, 'r')
        computers = f.read().split(" ")
        computers.sort()
    except:
        computers=()
        
    try:
        f = open(fileNameTeachers, 'r')
        teachers = f.read().split(" ")
        teachers.sort()
    except:
        teachers=()

    return dict(computers=computers,teachers=teachers)

@service.json   
@auth.requires_login()    
def wakeup():
    data = gluon.contrib.simplejson.loads(request.body.read())

    l=conecta()
    for i in data["pclist"]:
        h = Hosts(l,i,"","","")
        h.wakeup()

    return response.json({'success':'true'})

@service.json  
@auth.requires_login()     
def shutdown():
    try:
        server = xmlrpclib.ServerProxy("http://"+request.vars["host"]+":6800")
        s = server.shutdown()
        return dict(response="OK", host=request.vars["host"], message=s)
    except:
        return dict(response="fail", host=request.vars["host"], message="Surgió un error")
    

@service.json  
@auth.requires_login()   
def executeCommand():
    try:
        server = xmlrpclib.ServerProxy("http://"+request.vars["host"]+":6800")
        s = server.exec_command(request.vars["command"])
        return dict(response="OK", host=request.vars["host"], message=s)
    except:
        return dict(response="fail", host=request.vars["host"], message="Surgió un error")

@auth.requires_login()
def config():

    if not auth.user: redirect(URL(c='default',f='index'))

    configuracion=Config(cdb)
    configuracion.loadConfig()
       
    form=SQLFORM.factory(
          Field('m_server',type='string', label="Servidor correo (nombre:puerto)", length=50, default=configuracion.mail_server),
          Field('m_sender',type='string', label="Email de envio" , length=50, default=configuracion.mail_sender),
          Field('m_user', type='string', label="Usuario correo", length=50, default=configuracion.mail_user),
          Field('m_password',type='string',label="Contraseña correo" , length=30, default=configuracion.mail_password),
          Field ('m_receiver',type='string', label="Email receptor", length=50, default=configuracion.mail_receiver),
          Field ('a_thinclient',type='boolean', label="Alertar teclado/ratón thinclients", length=50, default=configuracion.alert_thinclient),
          Field ('l_email',type='boolean', label="Envio de correo resumen", length=50, default=configuracion.list_email),
          submit_button='Guardar Datos Configuración')

    if form.accepts(request.vars, session):
          response.flash = 'Procesando datos, espere'                    
          configuracion.saveConfig(form.vars.m_server,form.vars.m_sender, form.vars.m_user, form.vars.m_password, form.vars.m_receiver, form.vars.a_thinclient, form.vars.l_email)          
          redirect( URL( 'gestion', 'config')) 

    return dict(form=form)


@service.json
def sendMail():

    configuracion=Config(cdb)
    configuracion.loadConfig()
    configuracion.sendListReport()
    return configuracion.enviaMail('Desde controlies', 'Este es un mensaje enviado desde Controlies. Si le ha llegado es que todo esta correcto.')


def execCommand():
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
