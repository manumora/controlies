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
  dologin(usuario,maquina,tipohost)
  
@service.xmlrpc
def dologin(usuario,maquina,tipohost):
  cdb.sesiones.insert(usuario=usuario, host=maquina, tipohost=tipohost)

  
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
#    logfile = open("/tmp/"+host+".txt", "w")
#    logfile.write(request.body.read())
#    logfile.close()
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
    host=mydata["host"].upper()
    host=host[:host.index('.')]
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
	   
    output.write("<br><b>Clases y recursos aplicados</b><br><br>")      
    recursos=mydata["resource_statuses"]
    output.write("<table style='border: solid 1px #000000;width:95%'>")
    for item in recursos:
        eventos=recursos[item]['events']
        descripcion=recursos[item]['source_description']
        estado="OK"
        for evento in eventos:
            valor=evento['status']
            if valor == "failure" :
                 estado="ERROR"
                 estadoglobal="ERROR"
                 break	 
        if estado=="OK":                         			 
            output.write("<tr style='border: solid 1px #000000;'><td width='90%'>"+ descripcion +"</td><td>"+estado+"</td></tr>")
        else:
            output.write("<tr style='border: solid 1px #000000;'><td width='90%'><font color='red'>"+ descripcion +"</font></td><td><font color='red'>"+estado+"</font></td></tr>")
    output.write("</table><br><br></center>")
    
    fila=cdb((cdb.maquinas.host.upper()==host) & (cdb.maquinas.tipohost!='WINDOWS')).select().last()    
    if fila==None:
        pass
    else:		
        #Movemos el puntero del fichero al comienzo del mismo, ya que si no no se vuelca a la tabla.    
        output.seek(0)   
        fila.update_record(ultimopuppet=ahora,estadopuppet=estadoglobal,logpuppet=cdb.maquinas.logpuppet.store(output,filename=host))
    output.close()
        
    return "OK"
    
           
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
    if (raton=="1" or teclado=="1") and (configuracion.alert_thinclient==1): 
        
        #Busca ultimo estado que no sea "apagado", para comparar
        
        ultimo_estado=cdb((cdb.thinclients.host==host) & (cdb.thinclients.raton!="0") ).select(orderby=~cdb.thinclients.time).first()
        if ultimo_estado==None:
               ult_teclado="2"
               ult_raton="2"
        else:
               ult_teclado=ultimo_estado.teclado
               ult_raton=ultimo_estado.raton
               
        if (teclado=="1" and ult_teclado=="2") or (raton=="1" and ult_raton=="2"):
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

