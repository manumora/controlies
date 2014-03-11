# -*- coding: utf-8 -*-

from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils
from applications.controlies.modules.Hosts import Hosts

def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
        
    return dict()


def index_thinclients():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))

    return dict()

def index_aulas():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))

    return dict()

def form_user():
    return dict()
        


################## SEGUIMIENTO  ####################


@service.json
@auth.requires_login()
def list():

    fields = ['host','tipohost','ultimorefresco','ultimoarranque','ultimopkgsync','estadopaquetes','ultimopuppet','estadopuppet','alert']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
            
    sql="select id,host,tipohost,ultimorefresco,ultimoarranque,ultimopkgsync,estadopaquetes,ultimopuppet,estadopuppet,alert from maquinas where 1=1"
    where=""
    
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['tipohost']) != "None":
             where = where+" and tipohost like '%"+str(request.vars['tipohost'])+"%'"
    except LookupError:
       pass
        
    try:
       if str(request.vars['ultimorefresco']) != "None":
             where = where+" and ultimorefresco like '%"+str(request.vars['ultimorefresco'])+"%'"
    except LookupError:
       pass
       
    try:
       if str(request.vars['ultimoarranque']) != "None":
             where = where+" and ultimoarranque like '%"+str(request.vars['ultimoarranque'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['ultimopkgsync']) != "None":
             where = where+" and ultimopkgsync like '%"+str(request.vars['ultimopkgsync'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['estadopaquetes']) != "None":
             where = where+" and estadopaquetes like '%"+str(request.vars['estadopaquetes'])+"%'"
    except LookupError:
       pass          

    try:
       if str(request.vars['ultimopuppet']) != "None":
             where = where+" and ultimopuppet like '%"+str(request.vars['ultimopuppet'])+"%'"
    except LookupError:
       pass

    try:
       if str(request.vars['estadopuppet']) != "None":
             where = where+" and estadopuppet like '%"+str(request.vars['estadopuppet'])+"%'"
    except LookupError:
       pass


    fechaini='01-01-2000'
    try:
       if len(str(request.vars['fechaini'])) > 0 :
             fechaini=request.vars['fechaini'].replace("/","-")
    except LookupError:
       pass
      
    fechafin='01-01-2100'   
    try:
       if len(str(request.vars['fechafin'])) > 0 :
             fechafin=request.vars['fechafin'].replace("/","-")
    except LookupError:
       pass

    fechaini = formatearFecha(fechaini)
    fechafin = formatearFecha(fechafin)
    
    where=where+ " and ultimorefresco between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   
#    file = open('/sql.txt', 'w')
#    file.write(sql)
#    file.close()   

    consulta=cdb.executesql(sql)
    retorno=""
    for reg in consulta:
        retorno=retorno+reg[1]
        alertar="true" if reg[9]==1 else "false"
        row = {
                "id":reg[0],
                "cell":[reg[1],reg[2],reg[3],reg[4],reg[5],reg[6],reg[7],reg[8],alertar],
                "host":reg[1],
                "tipohost": reg[2],
                "ultimorefresco":reg[3],
                "ultimoarranque":reg[4],
                "ultimopkgsync":reg[5],
                "estadopaquetes":reg[6],
                "ultimopuppet":reg[7],
                "estadopuppet":reg[8],
                "alert":alertar
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from maquinas where 1=1 "+where)
    total = int(consulta[0][0])
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows } 
    
@service.json
def getFicheroPkgSync():
    
    id=int(request.vars["id"])                   
    fila=cdb(cdb.maquinas.id==id).select().first()
    if fila==None:
		texto="NO HAY DATOS"        
    else:		
       try:
          (filename, fichero) = cdb.maquinas.logpkgsync.retrieve(fila.logpkgsync)
          texto=fichero.read()
          fichero.close                 
       except IOError:
          texto="NO HAY DATOS"    
              
    return texto;

@service.json
def getFicheroLogPuppet():
    
    id=int(request.vars["id"])               
    fila=cdb(cdb.maquinas.id==id).select().first()
    if fila==None:
		texto="NO HAY DATOS"        
    else:		
       try:
          (filename, fichero) = cdb.maquinas.logpuppet.retrieve(fila.logpuppet)
          texto=fichero.read()
          fichero.close                         
       except:
          texto="NO HAY DATOS"    
        
    """sql="select logpuppet from maquinas where id="+str(id)
    consulta=cdb.executesql(sql)
    filename=consulta[0][0];        
    path = "applications/controlies/uploads"
    fichero=open(os.path.join(path, filename), 'rb')
    texto=fichero.read()
    fichero.close 
    """
        
    return texto;


@service.json
@auth.requires_login()
def list_thinclients_state():

    fields = ['host','time','raton','teclado']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
        
    sql="select distinct host from thinclients where 1=1"
    wherefiltro=""
    wherefecha=""
    whereestado=""
    try:
       if str(request.vars['host']) != "None":
             wherefiltro = wherefiltro+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['time']) != "None":
             wherefecha = wherefecha+" and time like '%"+str(request.vars['time'])+"%'"
    except LookupError:
       pass
       
    try:
       if str(request.vars['raton']) != "None":
             whereestado = whereestado+" and raton like '%"+str(request.vars['raton'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['teclado']) != "None":
             whereestado = whereestado+" and teclado like '%"+str(request.vars['teclado'])+"%'"
    except LookupError:
       pass          

    #Subconsulta para extraer el ultimo registro de cada rango.
    #wheresub=where+" and t1.id=(select id from thinclients t2 where t1.host=t2.host order by time desc limit 1)"
  
    sql = sql + wherefiltro+wherefecha+whereestado +" order by "+request.vars['sidx']+" "+request.vars['sord'] 

        
#    file = open('/tmp/sql.txt', 'w')
#    file.write(sql)
#    file.close()   


    consulta=cdb.executesql(sql)    
    posrecord=0
    for reg in consulta:        
        host=reg[0]
        sqlultimo="select id,host,time,teclado,raton from thinclients where host='"+host+"'"+wherefecha+" order by time desc limit 1"   
        sql="select id,host,time,teclado,raton from thinclients where host='"+host+"' "+wherefecha+whereestado+"   order by time desc limit 1"
        consulta_ultimo=cdb.executesql(sqlultimo) #devuelve el ultimo valor de ese thinclient en la fecha indicada
        consulta_host=cdb.executesql(sql) #devuelve una tupla o ninguna con el ultimo valor de ese thinclient
                                          #en ese estado de ratón y teclado
        if len(consulta_host)==1 :
            reg=consulta_host[0]
            reg_ultimo=consulta_ultimo[0]
            if reg[0]==reg_ultimo[0]:
                if (posrecord>=offset and posrecord<offset+pagesize) :
                    #Si el ultimo registro del thinclient en esa fecha coincide con el ultimo
                    #registro con ese estado de ratón y teclado, se incluye en la lista
                    row = {
                            "id":reg[0],
                            "cell":[reg[1],reg[2],reg[3],reg[4]],
                            "host":reg[1],
                            "time":reg[2],
                            "teclado":reg[3],
                            "raton":reg[4]                
                        }
                    rows.append(row)
                posrecord=posrecord+1

    total = posrecord   
    pages = int(total/pagesize) + 1    
        
    return { "page":page, "total":pages, "records":total, "rows":rows  } 


def traza(texto):
    
    file = open('/tmp/salida.txt', 'a')    
    file.write(texto)
    file.close()      

@service.json
@auth.requires_login()
def list_thinclient_detail():

    fields = ['host','time','raton','teclado']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])
    offset = (page-1) * pagesize

    sqlthc="select id,host,time,teclado,raton from thinclients where 1=1"    
    sqlses="select id,host,timelogin as time,usuario as teclado ,'' as raton from sesiones where 1=1"
    wherethc=""
    whereses=""
    try:
       if str(request.vars['host']) != "None":
             wherethc = wherethc+" and host like '%"+str(request.vars['host'])+"%'"
             whereses = whereses +" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass

    try:
       if str(request.vars['time']) != "None":
             wherethc = wherethc+" and time like '%"+str(request.vars['time'])+"%'"
    except LookupError:
       pass

    try:
       if str(request.vars['raton']) != "None":
             wherethc = wherethc+" and raton like '%"+str(request.vars['raton'])+"%'"
    except LookupError:
      pass

    try:
       if str(request.vars['teclado']) != "None":
             wherethc = wherethc+" and teclado like '%"+str(request.vars['teclado'])+"%'"
    except LookupError:
       pass

#    sql = sqlthc + wherethc + " order by time limit "+str(pagesize)+" offset "+str(offset)

    sql = sqlthc + wherethc+ " union " + sqlses + whereses+" order by time desc limit "+str(pagesize)+" offset "+str(offset)


#    file = open('/tmp/sql.txt', 'w')
#    file.write(sql)
#    file.close()   

    consulta=cdb.executesql(sql)
    
    for reg in consulta:
        row = {
                "id":reg[0],
                "cell":[reg[2],reg[3],reg[4]],
                "host": reg[1],
                "time":reg[2],
                "teclado":reg[3],
                "raton":reg[4]
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from ( "+ sqlthc + wherethc + " union "+ sqlses + whereses +")")

#    file = open('/tmp/sql.txt', 'w')
#    file.write("select count(*) as total from ( "+ sqlthc + wherethc + " union "+ sqlses + whereses +")")
#    file.close() 

    consulta=cdb.executesql("select count(*) as total from thinclients where 1=1 "+wherethc)
    total = int(consulta[0][0])
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows }

@service.json
@auth.requires_login()
def matriz_aula():

    aula = request.vars["prefijo"].upper()
    fecha = formatearFecha(request.vars['fecha'])

    profesor=aula+"-PRO"

    filas=[]
    
    sql="select host from maquinas where upper(host)='" + profesor + "'"
    consulta=cdb.executesql(sql)
    #Incluimos el servidor de aula
    if len(consulta) > 0 : 
       profesor=consulta[0][0]
       filas=addUnico(filas,profesor)
    
    #Incluimos los thinclients
    sql="select distinct host from thinclients where host like '"+aula+"-%' order by host"
    consulta=cdb.executesql(sql)    
    for reg in consulta:
        host=reg[0]
        filas=addUnico(filas,host)        
    
    #Incluimos los workstations
    sql="select distinct host from maquinas where host like '"+aula+"-%' and (tipohost='WORKSTATION' or tipohost='WINDOWS') order by host"
    #logea("/tmp/sql.txt",sql)
    consulta=cdb.executesql(sql)    
    for reg in consulta:
        host=reg[0]
        filas=addUnico(filas,host)                
            
    #Incluimos los portatiles
    sql="select distinct host from sesiones "
    sql=sql+"where upper(aula)=upper('"+aula+"') and tipohost='PORTATIL' and "
    sql=sql+" timelogin between '"+fecha+"' and date('"+fecha+"','+24 hours') order by host"
    consulta=cdb.executesql(sql)    
    for reg in consulta:
        host=reg[0]
        filas=addUnico(filas,host)        
    
    if len(filas) == 0:
        
        retorno= {"codigo": "ERROR", "mensaje": "No se ha encontrado nada referido al aula "+aula}
        
    else:
               
        horarios=[]
        #[['08:15','09:25','1Hora'],['09:26','10:20','2Hora'],['10:21','11:15','3Hora'],..... ]
        sql="select id,inicio,fin,descripcion from horarios order by inicio"
        consulta=cdb.executesql(sql)
        for reg in consulta:
           row = [ reg[1], reg[2], reg[3] ]
           horarios.append(row)
          
        rows=[]
        idrow=0
        for host in filas:
            celda=[]        
            row={"id":idrow, "host": host}
            for clase in horarios: 
                idclase=clase[2]
                datos=obtenerActividad(fecha,clase,host,aula)
                #contenido=""
                #for entrada in datos:
                #    contenido=contenido+entrada["time"]+"-"+entrada["teclado"]+"-"+entrada["raton"]+"\n"
                celda.append(datos)
                row[idclase]=datos
                
            row["cell"]= celda 
            rows.append(row)
            idrow=idrow+1
            
        userdata={ "columnas": horarios} 
        retorno= {"codigo": "OK", "page":1, "total":1, "records": len(horarios), "rows":rows, "userdata": userdata }
        
    return retorno

#Este es el formato a devolver: http://www.trirand.com/jqgridwiki/doku.php?id=wiki:retrieving_data#json_data

#Añade el elemento a la lista, si no está previamente
def addUnico(lista,elemento):
    
    try:
        i=lista.index(elemento)        
    except:
        lista.append(elemento)
    
    return lista
 

def obtenerActividad(fecha,clase,host,aula):

    sqlthc="select id,host,time,teclado,raton, 'thinclient' as tipo from thinclients where 1=1"    
    sqlses="select id,host,timelogin as time,usuario as teclado ,timelogout as raton, 'sesion' as tipo from sesiones where 1=1"
    wherethc=""
    whereses=""
    wherethc = wherethc+" and host ='"+host+"'"
    whereses = whereses +" and host ='"+host+"'"
    horaini=fecha+" "+clase[0]
    horafin=fecha+" "+clase[1]
    wherethc = wherethc+" and time between '"+horaini+"' and '"+horafin+"'"
    whereses = whereses+" and time between '"+horaini+"' and '"+horafin+"'"
    whereses = whereses+" and ( upper(aula)=upper('"+aula+"') or ifnull(aula,'')='' ) " 
    
    sql = sqlthc + wherethc+ " union " + sqlses + whereses+" order by time"
    
    #file = open('/tmp/sql.txt', 'w')
    #file.write(sql)
    #file.close()   

    consulta=cdb.executesql(sql)
    rows=[]

    for reg in consulta:
        
        hora=reg[2][11:16]
        if reg[5]=="thinclient":
            valor=reg[4]
        else:
            if reg[4]!= None:
                valor=reg[4][11:16]
            else:
                valor=""
                
        row = {
                "id":reg[0],
                "cell":[reg[1],hora,reg[3],valor,reg[5]],
                "host": reg[1],
                "time":hora,
                "teclado":reg[3],
                "raton":valor,
                "tipo": reg[5]
            }
        rows.append(row)
    
    return rows


def formatearFecha(fecha):
	return fecha[6:]+"-"+fecha[3:5]+"-"+fecha[0:2]    

@service.json
def cleanthinclients():

    retorno="OK"
    hoy=str(datetime.date.today())
    sql="delete from thinclients where time <= date('"+hoy+"','-1 months')"           
#    file = open('/tmp/sqlborrado.txt', 'w')
#    file.write(sql)
#    file.close()       
    try:
        cdb.executesql(sql)
        retorno="OK"
    except:
        retorno="fail"
 
    return dict(response=retorno)

@service.json
def getUserData():

    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","")
    response = u.getUserData()
    l.close()
    return dict(response=response)


    
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


@service.json
def borrarHost():

    retorno="OK"
    idhost=request.vars['id']
    try:
       cdb(cdb.maquinas.id == int(idhost)).delete()
       retorno="OK"
    except:
       retorno="fail"
              
    return dict(response=retorno)
 
@service.json
def toggleHostAlert():

    retorno="OK"
    idhost=request.vars['id']
    stateAlert=request.vars['state']
    #Ojo, en sqlite los boolean son integer
    sql="update maquinas set alert="+stateAlert+"  where id="+idhost
    
#    file = open('/tmp/sql.txt', 'w')
#    file.write(str(request.vars))
#    file.close()       

    try:
       cdb.executesql(sql)
       retorno="OK"
    except:
       retorno="fail"
    return dict(response=retorno)
 
def logea(fichero,texto):
 
   file = open(fichero, 'w')
   file.write(texto)
   file.close()   
