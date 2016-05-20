# coding: utf8
from applications.controlies.modules.Hosts import Hosts
from applications.controlies.modules.Rayuela2Ldap import Rayuela  
from applications.controlies.modules.SQLiteConnection import SQLiteConnection
from applications.controlies.modules.Laptops import Laptops
from applications.controlies.modules.LaptopsHistory import LaptopsHistory
from applications.controlies.modules.Config import Config
from applications.controlies.modules.Thinclients import Thinclients
from applications.controlies.modules.Utils import Utils
from applications.controlies.modules.Utils import LdapUtils
import applications.controlies.modules.websocket_messaging as WS

import xmlrpclib
import gluon.contrib.simplejson
from gluon.tools import Mail

import re
import cgi
import select
from applications.controlies.modules import ansi
from applications.controlies.modules.ansi2html import ansi2html
from applications.controlies.modules.SSHConnection import SSHConnection

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

    l=conecta()
    t = Thinclients(l,"","","","")
    computers1 = t.getAllComputersNode("group1")    
    computers2 = t.getAllComputersNode("group2")
    computers3 = t.getAllComputersNode("group3")
    computers4 = t.getAllComputersNode("group4")
    
    all = computers1["computers"]+computers2["computers"]+computers3["computers"]+computers4["computers"]
    for c in all:
        t2 = Thinclients(l,c,"","","")
        response = t2.move(c)
    
    l.close()

    c = SSHConnection("localhost","root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")
    if response != True:
        return dict()

    c.exec_command("if ! pgrep ssh-agent ; then eval $(ssh-agent -s); fi")
    #c.exec_command("ssh-add /var/web2py/applications/controlies/.ssh/id_rsa")
    c.close()
    return dict()


@service.json   
@auth.requires_login()
def set_alias():
    if(request.vars['name'].strip()==""):
        return dict(response="name")
    else:
        session.alias = request.vars['name'].strip()
        return dict(response="OK")

@service.json   
@auth.requires_login()
def chat():
    if not auth.user: redirect(URL(c='default',f='index'))

    l=conecta()
    session.domain = LdapUtils.getDomain(l)
    l.close()


    import random
    r = lambda: random.randint(0,255)
    color = ('#%02X%02X%02X' % (r(),r(),r()))
    session.color = color

    #WS.websocket_send('http://127.0.0.1:8888',session.domain+" ha entrado en la sala"+'<br/>','mykey','chat')    
    return dict()

@service.json   
@auth.requires_login()
def chat_send_message():
    try:
        alias = session.alias+"."+session.domain
    except:
        alias = session.domain
        
    try:
        if request.vars["text"].strip()!="":
            WS.websocket_send('http://172.23.36.5:8888/chat','<span style="color:'+session.color+'; font-weight:bold;">'+alias+"</span>: "+request.vars["text"]+'<br/>','mykey','chat')
    except:
        return dict(response="fail", message="No se pudo conectar con el servidor websocket.<br/>")

    return dict(response="OK")

    return dict(response="OK")

@service.json
@auth.requires_login()
def setChatSession():
    if not auth.user: redirect(URL(c='default',f='index'))
    return dict(response="OK")

@service.json   
@auth.requires_login()
def servidores_centro():
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

    s = xmlrpclib.Server("http://" + request.vars['classroom'] + ":8900")

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
    response = h.getListTriplets()
    l.close()
    return dict(response=response)


@service.json
@auth.requires_login()
def getSIATIC():
    l=conecta()
    h = Hosts (l,"","","","siatic-hosts")
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
    try:
        l=conecta()
        h = Hosts (l,"","","","laptop-hosts")    
        response = h.getListTriplets()
        l.close()
    except:
        response=[]

    return dict(response=response)

@service.json   
@auth.requires_login()    
def getLaptopsPupils():
    try:
        classroom = request.vars['classroom'].split("-")
        l=conecta()
        t = Thinclients(l,"","","","")
        computers = t.getAllComputersNode(classroom[0])
        response = computers["computers"]
    except:
        response=[]    

    return dict(response=response)

@service.json   
@auth.requires_login()    
def getLTSPStatus():
    try:
        rpcServer = xmlrpclib.ServerProxy("http://localhost:6969", allow_none=True)
    except:
        pass
    
    try:
        computers = rpcServer.get_computers()
    except:
        computers=()   

    try:
        teachers = rpcServer.get_teachers()
    except:
        teachers=()   
  
    try:
        laptops = rpcServer.get_laptops()
        numbers={}
        
        for i in laptops:
            classroom = i.split("-")
            
            if classroom[0] in numbers:
                numbers[classroom[0]] = int(numbers[classroom[0]])+1
            elif classroom[0]!="":
                numbers[classroom[0]] = 1  
         
    except:
        numbers={}

    return dict(computers=computers,teachers=teachers,laptops=numbers)

@service.json   
@auth.requires_login()    
def getLaptopsStatus():
    
    try:
        rpcServer = xmlrpclib.ServerProxy("http://localhost:6969", allow_none=True)
    except:
        pass

    try:
        pupils = rpcServer.get_pupils()
    except:
        pupils=()


    try:
        laptops = rpcServer.get_laptops()
    except:
        laptops=()
   
    return dict(computers=laptops, pupils=pupils)

@service.json   
@auth.requires_login()    
def wakeup():
    data = gluon.contrib.simplejson.loads(request.body.read())

    l=conecta()
    broadcast = LdapUtils.getBroadcast(l)
    for i in data["pclist"]:
        h = Hosts(l,i,"","","")
        h.wakeup(broadcast)

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
    


"""
def text2HTML(text):
    
    text2HTML = {'[1;30m' : '<span style="color:black">',
                 '[1;31m' : '<span style="color:red">', 
                 '[1;32m' : '<span style="color:green">',
                 '[1;33m' : '<span style="color:yellow">',
                 '[1;34m' : '<span style="color:blue">',
                 '[1;35m' : '<span style="color:purple">',
                 '[1;36m' : '<span style="color:cyan">',
                 '[1;37m' : '<span style="color:white">',
                 '[m' : '</span>'}

    print text2HTML['[1;34m']
    textcolor = text.split("m")[0]
    parseHTML()"""

@service.json  
@auth.requires_login()   
def executeCommand():
    """try:
        server = xmlrpclib.ServerProxy("http://"+request.vars["host"]+":6800")
        s = server.exec_command(request.vars["command"])
        return dict(response="OK", host=request.vars["host"], message=s)
    except:
        return dict(response="fail", host=request.vars["host"], message="Surgió un error")"""        

    c = SSHConnection(request.vars["host"],"root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")
    #response = c.connectWithoutPass("/home/manu/proyectos/controlies/applications/controlies/.ssh/id_rsa")

    try:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span> > <span style="font-size:10pt;">'+request.vars["command"]+'</span><br>','mykey','mygroup')
    except:
        return dict(response="fail", host=request.vars["host"], message="No se pudo conectar con el servidor websocket.<br/>")
            
    if response != True:
        return dict(response="fail", host=request.vars["host"], message="No se pudo conectar. ¿Está encendido el equipo? ¿Has establecido la relación de confianza?<br/>")
    
    channel = c.exec_command(request.vars["command"])
    
    import select
    while True:
        if channel.exit_status_ready():
            break
        rl, wl, xl = select.select([channel], [], [], 0.0)
        if len(rl) > 0:
            HTML_PARSER = ansi2html()
            html = HTML_PARSER.parse(channel.recv(1024))
            try:        
                WS.websocket_send('http://ldap:8888',html,'mykey','mygroup')
            except:
                pass

    WS.websocket_send('http://ldap:8888','<br>','mykey','mygroup')
    channel.close()
    c.close()
    return dict(response="OK", host=request.vars["host"], message="")

@service.json  
@auth.requires_login()   
def executeCommandLaptop():
    try:
        server = xmlrpclib.ServerProxy("http://ldap:6969")
        data = server.get_data_laptops(request.vars["host"])
    except:
        pass

    try:
        proxy = data[0]["proxy"]
        ip = data[0]["ip"]
    except:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>No se pudieron obtener los datos de conexión del equipo, ¿está encendido?','mykey','mygroup')
        return dict()

    c = SSHConnection(proxy,"root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")

    if response != True:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>No se pudo conectar con el servidor de aula. ¿Has establecido la relación de confianza?','mykey','mygroup')
        return dict()

    channel = c.exec_command('/usr/bin/python /usr/share/controlies-ltspserver/remoteCommand.py '+ip+' "'+request.vars["command"]+'" '+request.vars["host"])

    import select
    import time

    while True:
	#time.sleep(0.3)

        if channel.exit_status_ready():
            break

        rl, wl, xl = select.select([channel], [], [], 0.0)
        if len(rl) > 0:
            if channel.recv(1024).rstrip().strip()=="no_ssh":
                WS.websocket_send('http://ldap:8888','El servidor de aula no pudo conectar con el equipo. ¿Has establecido la relación de confianza?','mykey','mygroup')
                break                

            if channel.recv(1024).rstrip().strip()=="no_websocket":
                WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>El equipo no pudo conectar por websocket','mykey','mygroup')
                break   
                
    return dict()

@service.json  
@auth.requires_login()   
def getInfoComputers():
    try:
        server = xmlrpclib.ServerProxy("http://ldap:6969")
        data = server.get_data_laptops(request.vars["host"])
    except:
        data = []
        pass

    if not data:
        WS.websocket_send('http://ldap:8888','<br><span style="font-size:14pt;">'+request.vars["host"]+'</span><br> No hay información ¿El equipo está conectado?<br>','mykey','mygroup')
    else:
        WS.websocket_send('http://ldap:8888','<br><span style="font-size:14pt;">'+request.vars["host"]+'</span><br> -Conectado a: '+data[0]["proxy"]+'<br> -IP: '+data[0]["ip"]+'<br>','mykey','mygroup')

    return dict(response="OK", host=request.vars["host"], message="")

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
          Field ('a_teclado',type='boolean', label="Alertar teclado thinclients", length=50, default=True if configuracion.alert_teclado==1 else False),
          Field ('a_raton',type='boolean', label="Alertar raton thinclients", length=50, default=True if configuracion.alert_raton==1 else False),
          Field ('a_apagado',type='boolean', label="Alertar thinclients apagados", length=50, default=True if configuracion.alert_apagado==1 else False),
          Field ('l_email',type='boolean', label="Envio de correo resumen", length=50, default=True if configuracion.list_email==1 else False) ,
          submit_button='Guardar Datos Configuración')

    if form.accepts(request.vars, session):
          response.flash = 'Procesando datos, espere'                    
          configuracion.saveConfig(form.vars.m_server,form.vars.m_sender, form.vars.m_user, form.vars.m_password, form.vars.m_receiver, form.vars.a_teclado, form.vars.a_raton, form.vars.a_apagado, form.vars.l_email)          
          redirect( URL( 'gestion', 'config')) 

    return dict(form=form)


@service.json
def sendReportMail():

    configuracion=Config(cdb)
    configuracion.loadConfig()
    return configuracion.sendListReport()

@service.json
def sendTestMail():

    configuracion=Config(cdb)
    configuracion.loadConfig()
    return configuracion.enviaMail('Desde controlies', 'Este es un mensaje enviado desde Controlies. Si le ha llegado es que todo esta correcto.')


@service.json
def getConfigData():

    configuracion=Config(cdb)
    configuracion.loadConfig()
    response=configuracion.getConfigData()
    
    return dict(response=response)


@service.json
def getServerStatus():

    servidor=request.vars["server"]
    
    response=[ {"id": 1, "label": "Progreso", "type": "progress", "value": 75},
                 {"id": 2, "label": "Progreso 2", "type": "progress", "value": 30},   
                 {"id": 3, "label": "Servidor NFS", "type": "title"},
                 {"id": 4, "label": "Uso", "type": "text", "value": "Hola"},
                 {"id": 5, "label": "Estado", "type": "onoff", "value": "on"} ]
    
    s = xmlrpclib.Server("http://"+servidor+":6800");
    response = s.getServerMonitor()

    
    return dict(response=response)

@service.json
@auth.requires_login()    
def setConfigData():

    configuracion=Config(cdb)
    configuracion.loadConfig()    
    
    import gluon.contrib.simplejson
    
    #Los datos vienen en un string json y hay que reconstituirlos sobre un diccionario-lista python.
    data = gluon.contrib.simplejson.loads(request.vars["data"])
    
    try:
       a_teclado=False
       if str(data['a_teclado']) == "a_teclado":
             a_teclado=True
    except LookupError:
             pass
    try:
       a_raton=False
       if str(data['a_raton']) == "a_raton":
             a_raton=True
    except LookupError:
             pass
    try:
       a_apagado=False
       if str(data['a_apagado']) == "a_apagado":
             a_apagado=True
    except LookupError:
             pass
    try:
       l_email=False           
       if str(data['l_email']) == "l_email":       
             l_email=True
    except LookupError:
             pass      
             
    configuracion.saveConfig(data['m_server'],
                   data['m_sender'],
                   data['m_user'], 
                   data['m_password'], 
                   data['m_receiver'], 
                   a_teclado, 
                   a_raton, 
                   a_apagado, 
                   l_email,
                   data['horarios'])               
                   
    response = "OK"
    return dict(response = response)    

@service.json
@auth.requires_login()    
def dummy():

   response = "OK"
   return dict(response = response)    

@service.json
@auth.requires_login()    
def addMonitorizado():
  
    host=request.vars['host']
    fila=cdb(cdb.monitorizados.host == host).select().last()
    if fila == None :
       cdb.monitorizados.insert(host=host)
    retorno="OK"

@service.json
@auth.requires_login()    
def delMonitorizado():
  
    host=request.vars['host']
    try:
       cdb(cdb.monitorizados.host == host).delete()
       retorno="OK"
    except:
       retorno="fail"
              
@service.json
@auth.requires_login()    
def getMonitorizados():
	
    sql="select host from monitorizados"
    consulta=cdb.executesql(sql)
    return {"monitorizados": consulta}

def classroom_computers():
    
    return dict()

def execCommand():
    return dict()

def execCommandClassroom():
    return dict()

def infoComputers():
    return dict()

def friendshipSSH():
    return dict()

def friendshipSSH_form():
    return dict()

def routerCommands():
    return dict()

def routerCommands_form():
    return dict()

def form_chat():
    return dict()

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    #session.forget()
    return service()

@service.json
@auth.requires_login()
def setRelationshipSSH():

    if request.vars['type']=="testFields":
        if request.vars['passhost'].strip()=="":
            return dict(response="passhost")
        else:
            return dict(response="OK")

    try:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>','mykey','mygroup')
    except:
        return dict(response="fail", host=request.vars["host"], message="No se pudo conectar con el servidor websocket.<br/>")

    dir_ssh = '/var/web2py/applications/controlies'

    import subprocess
    p = subprocess.Popen('sshpass -p '+request.vars['passhost']+' ssh-copy-id -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i '+dir_ssh+'/.ssh/id_rsa.pub root@'+request.vars['host'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        HTML_PARSER = ansi2html()
        html = HTML_PARSER.parse(p.communicate()[0])
        WS.websocket_send('http://ldap:8888',html,'mykey','mygroup')
    except:
        pass

    if request.vars['passrouter'].strip():

        idRsaPub = open("/var/web2py/applications/controlies/.ssh/id_rsa.pub", "r").readline().replace("\n","").replace("\r","")

        c = SSHConnection(request.vars['host'],"root","")
        response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")

        if response != True:
            WS.websocket_send('http://ldap:8888',response+'<br>','mykey','mygroup')
            return dict(response = "OK")

        c.open_ftp()
        c.removeFile(dir_ssh+"/.ssh/controlIES_rsa.pub")
        c.removeFile(dir_ssh+"/.ssh/controlIES_rsa")
        c.putFile(dir_ssh+"/.ssh/id_rsa.pub","/root/.ssh/controlIES_rsa.pub")
        c.putFile(dir_ssh+"/.ssh/id_rsa","/root/.ssh/controlIES_rsa")
        c.exec_command("chmod 600 /root/.ssh/controlIES_rsa")
        #c.exec_command("sshpass -p "+request.vars['passrouter'].strip()+" ssh root@192.168.0.1 \"if ! grep -Fxq '"+idRsaPub+"' /tmp/root/.ssh/authorized_keys > /dev/null ; then echo '"+idRsaPub+"' >> /tmp/root/.ssh/authorized_keys; fi\"")

        p = subprocess.Popen('sshpass -p '+request.vars['passhost']+' ssh -A -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i '+dir_ssh+'/.ssh/id_rsa root@'+request.vars["host"]+' sshpass -p '+request.vars['passrouter']+' ssh-copy-id -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i /root/.ssh/controlIES_rsa.pub root@192.168.0.1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            HTML_PARSER = ansi2html()
            html = HTML_PARSER.parse(p.communicate()[0])
            WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">Router '+request.vars["host"]+'</span><br/>'+html,'mykey','mygroup')
        except:
            pass

        p = subprocess.Popen('sshpass -p '+request.vars['passhost']+' ssh -A -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i '+dir_ssh+'/.ssh/id_rsa root@'+request.vars["host"]+' sshpass -p '+request.vars['passrouter']+' ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.0.1 "nvram set sshd_authorized_keys=\''+idRsaPub.replace(" ","\\ ")+'\' nvram commit"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        c.removeFile("/root/.ssh/controlIES_rsa.pub")
        c.removeFile("/root/.ssh/controlIES_rsa")

        c.close()
    return dict(response = "OK")

    """c = SSHConnection(request.vars['host'],"root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")

    if not response:
        return dict(response = "YetSSH", host=request.vars["host"], message="Este host ya tiene relación de confianza<br/>") #Ya tenía establecida relación de confianza SSH

    try:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>','mykey','mygroup')
    except:
        return dict(response="fail", host=request.vars["host"], message="No se pudo conectar con el servidor websocket.<br/>")

    try:
        dir_ssh = "/var/web2py/applications/controlies"
        c.open_ftp()
        c.removeFile("/tmp/controlIES_rsa.pub")
        c.putFile(dir_ssh+"/.ssh/id_rsa.pub","/tmp/controlIES_rsa.pub")
        c.exec_command('cat /tmp/controlIES_rsa.pub >> /root/.ssh/authorized_keys')
        c.close_ftp()

        if request.vars['type']=="SIATIC" and request.vars['passrouter']:
            import subprocess

            channel = subprocess.Popen('ssh -A -t root@'+request.vars['hostname']+' sshpass -p '+request.vars['routerPass']+' ssh-copy-id root@192.168.0.1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            import select
            while True:
                if channel.exit_status_ready():
                    break
                rl, wl, xl = select.select([channel], [], [], 0.0)
                if len(rl) > 0:
                    HTML_PARSER = ansi2html()
                    html = HTML_PARSER.parse(channel.recv(1024))
                    try:
                        WS.websocket_send('http://ldap:8888',html,'mykey','mygroup')
                    except:
                        pass

            WS.websocket_send('http://ldap:8888','<br>','mykey','mygroup')
            channel.close()

    except:
        return dict(response = "Error")
        pass

    c.close()
    return dict(response = "OK")"""
    #ssh -A -t root@a35-pro ssh-copy-id root@192.168.0.1
    #ssh -A -t root@a02-pro sshpass -p TexFono1 ssh-copy-id root@192.168.0.1

def getChannel(channel, name):
    while True:
        if channel.exit_status_ready():
            break
        rl, wl, xl = select.select([channel], [], [], 0.0)
        if len(rl) > 0:
            HTML_PARSER = ansi2html()
            html = HTML_PARSER.parse(channel.recv(1024))
            try:
                if html=="":
                    html="<br/>"
                WS.websocket_send('http://ldap:8888',name+": "+html,'mykey','mygroup')
            except:
                pass

@service.json
@auth.requires_login()
def commandsAP():
    from applications.controlies.modules import paramiko2

    proxy_key = "/var/web2py/applications/controlies/.ssh/id_rsa"
    proxy_user=user="root"
    proxy_host=request.vars["host"]
    host="192.168.0.1"

    proxy_command = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s nc %s %s' % (proxy_key, proxy_user, proxy_host, host, 22)
    proxy = paramiko2.ProxyCommand(proxy_command)

    client = paramiko2.SSHClient()
    client.set_missing_host_key_policy(paramiko2.AutoAddPolicy())

    WS.websocket_send('http://ldap:8888','<br><span style="font-size:14pt;">'+request.vars["host"]+'</span><br>','mykey','mygroup')

    try:
        client.connect(proxy_host, username=user, key_filename="/var/web2py/applications/controlies/.ssh/id_rsa", timeout=5)
    except:
        WS.websocket_send('http://ldap:8888','<span style="font-size:10pt;">No se pudo conectar. ¿Está encendido el equipo? ¿Has establecido la relación de confianza?</span><br>','mykey','mygroup')
        return dict()

    try:
        client.connect(host, username=user, key_filename="/var/web2py/applications/controlies/.ssh/id_rsa", sock=proxy)
    except:
        WS.websocket_send('http://ldap:8888','<span style="font-size:10pt;">No se pudo conectar con el punto de acceso. ¿Está encendido? ¿Has establecido la relación de confianza?</span><br>','mykey','mygroup')
        return dict()

    if request.vars["command"]=="getData":
        #stdin, stdout, stderr = client.exec_command('hostname')
        channel = client.get_transport().open_session()
        channel.exec_command('nvram get router_name')
        getChannel(channel, "Router name")

        WS.websocket_send('http://ldap:8888','------------<br/>Red 2.4Ghz<br/>','mykey','mygroup')

        channel = client.get_transport().open_session()
        channel.exec_command('nvram get wl0_ssid')
        getChannel(channel, "SSID")

        channel = client.get_transport().open_session()
        channel.exec_command('nvram get wl0_wpa_psk')
        getChannel(channel, "Password")

        channel = client.get_transport().open_session()
        channel.exec_command('cat /sys/devices/virtual/net/ra0/operstate')
        getChannel(channel, "Estado")

        WS.websocket_send('http://ldap:8888','------------<br/>Red 5Ghz<br/>','mykey','mygroup')

        channel = client.get_transport().open_session()
        channel.exec_command('nvram get wl1_ssid')
        getChannel(channel, "SSID")

        channel = client.get_transport().open_session()
        channel.exec_command('nvram get wl1_wpa_psk')
        getChannel(channel, "Password")

        channel = client.get_transport().open_session()
        channel.exec_command('cat /sys/devices/virtual/net/ba0/operstate')
        getChannel(channel, "Estado")

        #WS.websocket_send('http://ldap:8888','<br>','mykey','mygroup')
        channel.close()
        client.close()

    if request.vars["command"]=="enableWifi":
        channel = client.get_transport().open_session()
        channel.exec_command('ifconfig ra0 up; ifconfig ba0 up')
        WS.websocket_send('http://ldap:8888','Wifi activada<br/>','mykey','mygroup')

    if request.vars["command"]=="disableWifi":
        channel = client.get_transport().open_session()
        #channel.exec_command('setuserpasswd root SAVISA34')
        channel.exec_command('ifconfig ra0 down; ifconfig ba0 down')
        WS.websocket_send('http://ldap:8888','Wifi desactivada<br/>','mykey','mygroup')

    return dict(response = "OK")

@service.json
@auth.requires_login()
def setDataAP():
    if request.vars["nameAP"].strip()=="" and request.vars["passroot"].strip()=="" and request.vars["ssidA"].strip()=="" and request.vars["passA"].strip()=="" and request.vars["ssidB"].strip()=="" and request.vars["passB"].strip()=="" and request.vars["nameAPcheck"]=="" and request.vars["ssidAcheck"]=="" and request.vars["ssidBcheck"]=="" and request.vars["passAcheck"]=="" and request.vars["passBcheck"]=="":
        return dict(response = "noData")

    if request.vars["passA"].strip()!="":
        if len(request.vars["passA"])<8 or len(request.vars["passA"])>63:
            return dict(response = "wrongLength")

    if request.vars["passB"].strip()!="":
        if len(request.vars["passB"])<8 or len(request.vars["passB"])>63:
            return dict(response = "wrongLength")

    from applications.controlies.modules import paramiko2

    proxy_key = "/var/web2py/applications/controlies/.ssh/id_rsa"
    proxy_user=user="root"
    proxy_host=request.vars["host"]
    host="192.168.0.1"

    proxy_command = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s nc %s %s' % (proxy_key, proxy_user, proxy_host, host, 22)
    proxy = paramiko2.ProxyCommand(proxy_command)

    client = paramiko2.SSHClient()
    client.set_missing_host_key_policy(paramiko2.AutoAddPolicy())

    WS.websocket_send('http://ldap:8888','<br><span style="font-size:14pt;">'+request.vars["host"]+'</span><br>','mykey','mygroup')

    try:
        client.connect(proxy_host, username=user, key_filename="/var/web2py/applications/controlies/.ssh/id_rsa", timeout=5)
    except:
        WS.websocket_send('http://ldap:8888','<span style="font-size:10pt;">No se pudo conectar. ¿Está encendido el equipo? ¿Has establecido la relación de confianza?</span><br>','mykey','mygroup')
        return dict(response = "OK")

    try:
        client.connect(host, username=user, key_filename="/var/web2py/applications/controlies/.ssh/id_rsa", sock=proxy)
    except:
        WS.websocket_send('http://ldap:8888','<span style="font-size:10pt;">No se pudo conectar con el punto de acceso. ¿Está encendido? ¿Has establecido la relación de confianza?</span><br>','mykey','mygroup')
        return dict(response = "OK")

    if request.vars["nameAP"].strip()!="" or request.vars["nameAPcheck"]=="on":
        if request.vars["nameAPcheck"]=="on":
            request.vars["nameAP"] = request.vars["host"]+request.vars["nameAP"]

        channel = client.get_transport().open_session()
        channel.exec_command('nvram set router_name="'+request.vars["nameAP"].strip()+'"; nvram set wan_hostname="'+request.vars["nameAP"].strip()+'"; nvram commit;')
        WS.websocket_send('http://ldap:8888','Nombre del punto de acceso actualizado<br/>','mykey','mygroup')

    if request.vars["passroot"].strip()!="":
        channel = client.get_transport().open_session()
        channel.exec_command('setuserpasswd root '+request.vars["passroot"].strip())
        WS.websocket_send('http://ldap:8888','Password de administrador actualizado<br/>','mykey','mygroup')

    if request.vars["ssidA"].strip()!="" or request.vars["ssidAcheck"]=="on":
        if request.vars["ssidAcheck"]=="on":
            request.vars["ssidA"] = request.vars["host"]+request.vars["ssidA"]

        channel = client.get_transport().open_session()
        channel.exec_command('nvram set wl0_ssid="'+request.vars["ssidA"].strip()+'"; nvram commit;')
        WS.websocket_send('http://ldap:8888','SSID 2.4 Ghz actualizado<br/>','mykey','mygroup')

    if request.vars["passA"].strip()!="" or request.vars["passAcheck"]=="on":
        if request.vars["passAcheck"]=="on":
            request.vars["passA"] = request.vars["host"]+request.vars["passA"]

        channel = client.get_transport().open_session()
        channel.exec_command('nvram set wl0_wpa_gtk_rekey="3600"; nvram set wl0_crypto="tkip+aes"; nvram set wl0_akm="psk2"; nvram set wl0_security_mode="psk2"; nvram set wl0_closed="0" nvram set wl0_wpa_psk="'+request.vars["passA"].strip()+'"; nvram commit;')
        WS.websocket_send('http://ldap:8888','Password 2.4 Ghz actualizado<br/>','mykey','mygroup')

    if request.vars["ssidB"].strip()!="" or request.vars["ssidBcheck"]=="on":
        if request.vars["ssidBcheck"]=="on":
            request.vars["ssidB"] = request.vars["host"]+request.vars["ssidB"]

        channel = client.get_transport().open_session()
        channel.exec_command('nvram set wl1_ssid="'+request.vars["ssidB"].strip()+'_B"; nvram commit;')
        WS.websocket_send('http://ldap:8888','SSID 5 Ghz actualizado<br/>','mykey','mygroup')

    if request.vars["passB"].strip()!="" or request.vars["passBcheck"]=="on":
        if request.vars["passBcheck"]=="on":
            request.vars["passB"] = request.vars["host"]+request.vars["passB"]

        channel = client.get_transport().open_session()
        channel.exec_command('nvram set wl1_wpa_gtk_rekey="3600"; nvram set wl1_crypto="tkip+aes"; nvram set wl1_akm="psk2"; nvram set wl1_security_mode="psk2"; nvram set wl1_closed="0"; nvram set wl1_wpa_psk="'+request.vars["passB"].strip()+'"; nvram commit;')
        WS.websocket_send('http://ldap:8888','Password 5 Ghz actualizado<br/>','mykey','mygroup')

    channel = client.get_transport().open_session()
    channel.exec_command('reboot')
    WS.websocket_send('http://ldap:8888','Reiniciando AP...<br/>','mykey','mygroup')

    return dict(response = "OK")
    """try:
        WS.websocket_send('http://ldap:8888','<span style="font-size:14pt;">'+request.vars["host"]+'</span><br>','mykey','mygroup')
    except:
        return dict(response="fail", host=request.vars["host"], message="No se pudo conectar con el servidor websocket.<br/>")

    dir_ssh = '/var/web2py/applications/controlies'

    import subprocess
    comando = 'ssh -v -A -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i '+dir_ssh+'/.ssh/id_rsa root@'+request.vars['host']+' ssh -A -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@192.168.0.1 nvram get wl0_wpa_psk'
    #comando = 'ssh -i '+dir_ssh+'/.ssh/id_rsa root@'+request.vars['host']+' ls /etc'
    c = SSHConnection("localhost","root","")
    response = c.connectWithoutPass("/var/web2py/applications/controlies/.ssh/id_rsa")
    if response != True:
        return dict()

    channel = c.exec_command(comando)
    WS.websocket_send('http://ldap:8888',comando,'mykey','mygroup')
    import select
    while True:
        WS.websocket_send('http://ldap:8888',channel.recv(1024),'mykey','mygroup')
        if channel.exit_status_ready():
            break
        rl, wl, xl = select.select([channel], [], [], 0.0)
        if len(rl) > 0:
            HTML_PARSER = ansi2html()
            html = HTML_PARSER.parse(channel.recv(1024))
            try:
                WS.websocket_send('http://ldap:8888',html,'mykey','mygroup')
            except:
                pass

    WS.websocket_send('http://ldap:8888','<br>','mykey','mygroup')
    channel.close()
    c.close()

    return dict(response = "OK")
    return dict(response = "OK")"""
