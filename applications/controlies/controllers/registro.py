# coding: utf8
# intente algo como

import datetime
import yaml
import StringIO
from applications.controlies.modules.Config import Config

def index(): return dict(message="hello from registro.py")

def login():
  session.forget(response)
  
  usuario=request.vars['usuario']
  maquina=request.vars['maquina']
  tipohost=request.vars['tipohost']
  #Si viene el parametro aula, lo cogemos.
  #Si no viene, o viene vacio, lo inferimos a partir del nombre de la máquina.
  try:
       aula=request.vars['aula']
  except LookupError:
       aula=""
  if aula=="" : aula=getAula(maquina)
  dologin(usuario,maquina,tipohost,aula)

def getAula(host):
  pos=host.find("-")
  if pos != -1:
      aula=host[0:pos]
  else: # No hay "-", por tanto no podemos idenfificar el aula a la que pertenece, ya que la norma dice que
         # es aXX-oYY, siendo aXX el auula
     aula=""
  return aula

@service.xmlrpc
def dologin(usuario,maquina,tipohost,aula):
  cdb.sesiones.insert(usuario=usuario, host=maquina, tipohost=tipohost, aula=aula)

  
def logout():
  session.forget(response)
  
  usuario=request.vars['usuario']
  maquina=request.vars['maquina']
  dologout(usuario,maquina)
  
@service.xmlrpc
def dologout(usuario,maquina):
  ahora=datetime.datetime.today()
  fila=cdb((cdb.sesiones.usuario==usuario) & (cdb.sesiones.host==maquina) & (cdb.sesiones.timelogin.year()==ahora.year) & (cdb.sesiones.timelogin.month()==ahora.month) & (cdb.sesiones.timelogin.day()==ahora.day)).select().last()
  if fila != None :
     fila.update_record(timelogout=ahora)
     return "OK"
  else :
     return "Not"

def actualizahost():
    session.forget(response)
    host=request.vars["host"]
    tipohost=request.vars["tipohost"]
    ultimoarranque=request.vars["ultimoarranque"]
    #Estado paquetes puede venir o no, en ese caso damos un valor por defecto ''
    ultimopkgsync=request.vars.get("ultimopkgsync",'')
    estadopaquetes=request.vars.get("estadopaquetes",'')
    doactualizahost(host,tipohost,ultimoarranque,ultimopkgsync,estadopaquetes)

@service.xmlrpc
def doactualizahost(host,tipohost,ultimoarranque,ultimopkgsync,estadopaquetes): 
    ahora=datetime.datetime.today()
    fila=cdb((cdb.maquinas.host==host) & (cdb.maquinas.tipohost==tipohost)).select().last()
    if fila==None:
      if estadopaquetes!='':
           cdb.maquinas.insert(host=host,tipohost=tipohost,ultimorefresco=ahora,ultimoarranque=ultimoarranque,
                         ultimopkgsync=ultimopkgsync,estadopaquetes=estadopaquetes)   
      else:
           cdb.maquinas.insert(host=host,tipohost=tipohost,ultimorefresco=ahora,ultimoarranque=ultimoarranque)
    else:
      
      if fila.alert==1 and fila.ultimoarranque.strftime("%Y-%m-%d %H:%M")!=ultimoarranque[0:16]: 
             # Si está activada la alerta para ese host y es un nuevo arranque, se envia el mensaje de correo de alerta de encendido.
             # Para ver si es un nuevo arranque, comparamos las fechas de ultima arranque, desechando los segundos.
            configuracion=Config(cdb)
            configuracion.loadConfig()
            mensaje="Alerta: ha sido encendido el host monitorizado "+host+" con fecha "+ahora.strftime("%d/%m/%Y %H:%M")+"\n"
            configuracion.enviaMail("Encendido de "+host, mensaje)
                       
      if estadopaquetes!='':            
           fila.update_record(ultimorefresco=ahora, tipohost=tipohost, ultimopkgsync=ultimopkgsync,
                           ultimoarranque=ultimoarranque,
                           estadopaquetes=estadopaquetes)
      else:
           fila.update_record(ultimorefresco=ahora, tipohost=tipohost, ultimoarranque=ultimoarranque)
    return "OK"
           
          
def actualizalogpkgsync():
	
    session.forget(response)    
    host=request.args(0)
    doactualizalogpkgsync(host,request.args(0),request.body)
    
    
@service.xmlrpc
def doactualizalogpkgsync(host, filename, filetext):

    fila=cdb((cdb.maquinas.host==host) & (cdb.maquinas.tipohost!='WINDOWS') ).select().last()    
    if fila==None:
        pass
    else:		
	fila.update_record(
           logpkgsync=cdb.maquinas.logpkgsync.store(filetext,
           filename=filename))
    return "OK"



def actualizalogwpkg():

    session.forget(response)
    host=request.args(0)
    doactualizalogwpkg(host,request.args(0),request.body)

@service.xmlrpc
def doactualizalogwpkg(host, filename, filetext):

    fila=cdb((cdb.maquinas.host==host) & (cdb.maquinas.tipohost=='WINDOWS')).select().last()
    if fila==None:
        pass
    else:
        fila.update_record(
           logpkgsync=cdb.maquinas.logpkgsync.store(filetext,
           filename=filename))
    return "OK"


def construct_ruby_object(loader, suffix, node):
    return loader.construct_yaml_map(node)

def construct_ruby_sym(loader, node):
    return loader.construct_yaml_str(node)
     
def actualizalogpuppet():
    session.forget(response)
    doactualizalogpuppet(request.body)

@service.xmlrpc
def doactualizalogpuppet(filetext):

    ahora=datetime.datetime.today()
    yaml.add_multi_constructor(u"!ruby/object:", construct_ruby_object)
    yaml.add_constructor(u"!ruby/sym", construct_ruby_sym)
    mydata = yaml.load(filetext)
    host=mydata["host"]
    host_original=host[:host.index('.')]
    host=host_original.upper()
    #En host_original está el nombre en minúsculas(asi lo manda siempre puppet), y en host en mayúsculas.
    estado="OK"
    estadoglobal="OK"
    output = StringIO.StringIO()
    logs=mydata["logs"]
    output.write("<center><br><b>Logs de puppet</b><br><br>")   
    for item in logs:
       output.write("<table style='border: solid 1px #000000;width:95%;'>")
       if 'file' in item:
            output.write("<tr style='border: solid 1px #000000;'><td width='10%'>File</td><td>"+item['file']+":"+str(item['line'])+"</td></tr>")
                        
       output.write("<tr style='border: solid 1px #000000;'>")
       if item['level'] == 'err' :	   
           estadoglobal="ERROR"
           output.write("<td width='10%'><font color='red'>Level</font></td>")       
           output.write("<td><font color='red'>"+item['level']+"</font></td>")
       else:
           output.write("<td width='10%'>Level</td>")       
           output.write("<td>"+item['level']+"</td>")
       output.write("</tr>")           
       output.write("<tr><td width='10%'>Message</td><td>"+item['message']+"</td></tr>")
       output.write("</table><br>")
       if item['message'][:45] == "Could not retrieve catalog from remote server":
               # Could not retrieve catalog from remote server: SSL_connect SYSCALL returned=5 errno=0 state=SSLv2/v3 read server hello A"
               #Si se encuentra este mensaje quiere decir que no ha podido contactar con el servidor debido a un intermitente bug de puppet no corregido
               #En ese caso, lo mejor es abortar y actuar como si nunca hubiese habido intento de actualización. 
           return "OK"
	   
    output.write("<br><b>Clases y recursos aplicados</b><br><br>")      
    recursos=mydata["resource_statuses"]
    output.write("<table style='border: solid 1px #000000;width:95%'>")
    clases_todas=[]
    clases_error=[]
        
    for item in recursos:
        eventos=recursos[item]['events']
#       El campo source_description es obsoleto, ya no se usa en puppet
#       descripcion=recursos[item]['source_description']
        file=recursos[item]['file'] 
        if file != None:
          estado="OK"
          if file[:20] == "/etc/puppet/modules/" :
              #Es un modulo en la forma /etc/puppet/modules/config-iceweasel-firefox/manifests/init.pp. Lo quedamos en modules/config-iceweasel-firefox
              file=file[12:-18]
          elif file[:22] == "/etc/puppet/manifests/" :
              file=file[12:-3]
        else:  
           file=""
        descripcion=file+"/"+recursos[item]['resource'] 
              
        #El nombre de la clase es todo lo posterior al ultimo "/" del nombre del fichero
        pos=file.rfind("/")
        if pos != -1 :
            clase=file[pos+1:]
        else: #En los recursos donde no hay nombre de fichero, es el nombre del recurso
            clase=recursos[item]['resource']

        clases_todas.append(clase)        
        for evento in eventos:
                valor=evento['status']
                if valor == "failure" :
                       clases_error.append(clase)
                       estado="ERROR"
                       estadoglobal="ERROR"
                       break
                 
        if estado=="OK":                         			 
            output.write("<tr style='border: solid 1px #000000;'><td width='90%'>"+ descripcion +"</td><td>"+estado+"</td></tr>")
        else:
            output.write("<tr style='border: solid 1px #000000;'><td width='90%'><font color='red'>"+ descripcion +"</font></td><td><font color='red'>"+estado+"</font></td></tr>")
           
    output.write("</table><br><br></center>")
    
    fila=cdb((cdb.maquinas.host.upper()==host.upper()) & (cdb.maquinas.tipohost!='WINDOWS')).select().last()    
    if fila==None:
        pass
    else:		
        #Movemos el puntero del fichero al comienzo del mismo, ya que si no no se vuelca a la tabla.    
        output.seek(0)   
        fila.update_record(ultimopuppet=ahora,estadopuppet=estadoglobal,logpuppet=cdb.maquinas.logpuppet.store(output,filename=host))
    output.close()
     
    #Sep/2018: Este código se comenta porque ya no vamos a hacer este seguimiento: No lo usa nadie y penaliza mucho el rendimiento de la BBDD
    #Insertamos todas las clases recopiladas, con el estado pertinente: ok (si todo va bien), error (si alguno de los
    # recursos fallo). Previamente borramos todas las clases anteriormente asociadas a dicho host.    
    #limpiar_clases(host)
    #for clase in clases_todas:    
    #    estado="ERROR" if clase in clases_error else "OK"
    #    inserta_clase(clase,host_original,ahora,estado)
   
    #Se purgan las tablas de clases para limpiar todo lo almacenado
    purgar_clases()    
    
    return "OK"
 

#Divide un recurso en sus partes, separandolo por "/" a excepcion de que los  "/" esten dentro de unos "[...]"
#Devuelve un array de strings
# Descripcion: "/Stage[main]/Clase-especifica-squeeze/Restringe_impresora[ML-1210]/Exec[restringe-impresora-ML-1210]"
def split_source(descripcion):
    
    sources=[]
    anidamiento=0
    clase=""
    for car in descripcion[1:]:
        if car == "[" : anidamiento=anidamiento+1
        elif car == "]" : anidamiento=anidamiento-1
        
        if car == "/" and anidamiento == 0:
            sources.append(clase)
            clase=""
        else:
            clase=clase+car
    if clase != "":
        sources.append(clase)
        
    return sources[1:-1]

           
def actualizathinclient():
    session.forget(response)
    host=request.vars["host"]
    raton=request.vars["raton"]
    teclado=request.vars["teclado"]
    doactualizathinclient(host, raton, teclado)
    
@service.xmlrpc
def doactualizathinclient(host, raton, teclado):

    ahora=datetime.datetime.today()
    
    
    #Ver si hay que mandar emails, siempre que traiga informacion
    configuracion=Config(cdb)
    configuracion.loadConfig()    
    if (raton=="1" or teclado=="1") and (configuracion.alert_teclado==1 or configuracion.alert_raton==1): 
        
        #Busca ultimo estado que no sea "apagado", para comparar
        
        ultimo_estado=cdb((cdb.thinclients.host==host) & (cdb.thinclients.raton!="0") ).select(orderby=~cdb.thinclients.time).first()
        if ultimo_estado==None:
               ult_teclado="2"
               ult_raton="2"
        else:
               ult_teclado=ultimo_estado.teclado
               ult_raton=ultimo_estado.raton
               
        if (teclado=="1" and ult_teclado=="2" and configuracion.alert_teclado==1) or (raton=="1" and ult_raton=="2" and configuracion.alert_raton==1):
               mensaje="Aviso fallo teclado/ratón en thinclient "+host+" ("+ahora.strftime("%d/%m/%Y %H:%M")+")\n\n"
               est_teclado="Conectado" if teclado=="2" else "Desconectado"
               est_raton="Conectado" if raton=="2" else "Desconectado"
               mensaje=mensaje+"\tTeclado: "+est_teclado+"\n"
               mensaje=mensaje+"\tRaton: "+est_raton+"\n"
               configuracion.enviaMail('Aviso de thinclient '+host, mensaje)
        
    fila=cdb(cdb.thinclients.host==host).select(orderby=~cdb.thinclients.time).first()    
    if fila==None:
        cdb.thinclients.insert(host=host,time=ahora,raton=raton,teclado=teclado)  
    else:
      if fila.raton == "0":
         hora1=fila.time
         hora2=ahora
         diferencia=hora2-hora1
         if diferencia.seconds > 300 : #Si han pasado mas de 5 minutos es otro encendido
             cdb.thinclients.insert(host=host,time=ahora,raton=raton,teclado=teclado)  
         else:    	
             fila.update_record(time=ahora, raton=raton, teclado=teclado)
      else:
         cdb.thinclients.insert(host=host,time=ahora,raton=raton,teclado=teclado)  
        
    return "OK"

def actualizalogprinter():
    session.forget(response)
    impresora=request.vars["impresora"]
    jobid=request.vars["jobid"]
    usuario=request.vars["usuario"]
    host=request.vars["host"]
    trabajo=request.vars["trabajo"]
    paginas=request.vars["paginas"]
    copias=request.vars["copias"]
    total=int(paginas)*int(copias)
    tamanio=request.vars["tamanio"]
    dologprinter(impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio)
    
@service.xmlrpc
def dologprinter(impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio):

    cdb.logprinter.insert(impresora=impresora,jobid=jobid,usuario=usuario,host=host,trabajo=trabajo,paginas=paginas,copias=copias,total=total, tamanio=tamanio)
    return "OK"


def checkapagado():
    session.forget(response)
    host=request.vars["host"]
    docheckapagado(host)
    
@service.xmlrpc
def docheckapagado(host):

    ahora=datetime.datetime.today()
    
    #Ver si hay que mandar emails, siempre que traiga informacion
    configuracion=Config(cdb)
    configuracion.loadConfig()    
    if (configuracion.alert_apagado==1): 
    
        enviar_mensaje=False
        ultimos_estados=cdb(cdb.thinclients.host==host).select(orderby=~cdb.thinclients.time, limitby=(0, 2)).as_list()
        
        #Si hay algun estado anterior.... miramos si ha pasado de encendido->apagado.       
        if len(ultimos_estados)>0 :
            #Si el ultimo vale 0, estaba apagado.
            if (ultimos_estados[0]["raton"]=="0"):
               if len(ultimos_estados)>1:    #Si hay penultimo
                   #Si no vale 0, estaba encendido y ahora apagado. Hay que avisar de que está apagado.
                   if (ultimos_estados[1]["raton"]!="0"):
                       enviar_mensaje=True
               else:
                   #Si no hay penúltimo, avisamos de que está apagado.
                   enviar_mensaje=True           
                   
            if enviar_mensaje: 
                  mensaje="El thinclient "+host+" parece apagado o bloqueado ("+ahora.strftime("%d/%m/%Y %H:%M")+")\n\n"
                  configuracion.enviaMail('Aviso de thinclient '+host+" apagado", mensaje)


    return "OK"
    

def inserta_clase(clase, host, time, resultado):
        
    if clase != "": 
        tipohost=getTipo(host)    
        if tipohost != "":      
            fila=cdb((cdb.clases_puppet.clase==clase) & (cdb.clases_puppet.tipohost==tipohost)).select().first()
            if fila==None:
                clase_id=cdb.clases_puppet.insert(time=time,clase=clase,tipohost=tipohost)
                fila=cdb(cdb.clases_puppet.clase==clase).select()
            else:
                clase_id=fila.id
                        
            filahost=cdb((cdb.clases_puppet_host.id_clase==clase_id) & (cdb.clases_puppet_host.host==host)).select().first()
            if filahost==None:
                cdb.clases_puppet_host.insert(time=time,id_clase=clase_id, host=host,resultado=resultado)        
            else:
                filahost.update_record(time=time,resultado=resultado) 

#Elimina todas las clases asociadas a un host
def limpiar_clases(host):
    
    sql="delete from clases_puppet_host where host='" +host+"'"
    try:
        cdb.executesql(sql)
    except:
        pass
    
def purgar_clases():

    sql="delete from clases_puppet_host"
    try:
        cdb.executesql(sql)
    except:
        pass

    sql="delete from clases_puppet"
    try:
        cdb.executesql(sql)
    except:
        pass

def getTipo(host):
    
    fila=cdb(cdb.maquinas.host.upper()==host.upper()).select().first()
    if fila==None:
        tipo=""
    else:
        tipo=fila.tipohost

    return tipo
    
def logea(fichero, mensaje):

    logfile = open("/tmp/"+fichero+".txt", "a")
    logfile.write(mensaje+"\n")
    logfile.close()

