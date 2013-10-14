# coding: utf8

from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils

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


################## SEGUIMIENTO  ####################


@service.json
@auth.requires_login()
def list():

    fields = ['host','tipohost','ultimorefresco','ultimoarranque','ultimopkgsync','estadopaquetes','ultimopuppet','estadopuppet']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
            
    sql="select id,host,tipohost,ultimorefresco,ultimoarranque,ultimopkgsync,estadopaquetes,ultimopuppet,estadopuppet from maquinas where 1=1"
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
             fechaini=str(request.vars['fechaini'])
    except LookupError:
       pass
      
    fechafin='01-01-2100'   
    try:
       if len(str(request.vars['fechafin'])) > 0 :
             fechafin=str(request.vars['fechafin'])
    except LookupError:
       pass

    fechaini = formatearFecha(fechaini)
    fechafin = formatearFecha(fechafin)
    
    where=where+ " and ultimorefresco between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   
    
#    file = open('/tmp/sql.txt', 'w')
#    file.write(sql)
#    file.close()   

    consulta=cdb.executesql(sql)
    retorno=""
    for reg in consulta:
        retorno=retorno+reg[1]
        row = {
                "id":reg[0],
                "cell":[reg[1],reg[2],reg[3],reg[4],reg[5],reg[6],reg[7],reg[8]],
                "host":reg[1],
                "tipohost": reg[2],
                "ultimorefresco":reg[3],
                "ultimoarranque":reg[4],
                "ultimopkgsync":reg[5],
                "estadopaquetes":reg[6],
                "ultimopuppet":reg[7],
                "estadopuppet":reg[8],
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from maquinas where 1=1 "+where)
    total = int(consulta[0][0])   
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows  } 
    
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
        
    sql="select id,host,time,teclado,raton from thinclients t1 where 1=1"
    where=""
    whereestado=""
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['time']) != "None":
             where = where+" and time like '%"+str(request.vars['time'])+"%'"
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
    wheresub=where+" and t1.id=(select id from thinclients t2 where t1.host=t2.host order by time desc limit 1)"
  
    sql = sql + wheresub + whereestado +" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)

        
#    file = open('/tmp/sql.txt', 'w')
#    file.write(sql)
#    file.close()   


    consulta=cdb.executesql(sql)

    for reg in consulta:
        row = {
                "id":reg[0],
                "cell":[reg[1],reg[2],reg[3],reg[4]],
                "host":reg[1],
                "time":reg[2],
                "teclado":reg[3],
                "raton":reg[4]                
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total,id from thinclients t1 where 1=1 "+wheresub+whereestado)
    total = int(consulta[0][0])   
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows  } 


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

    file = open('/tmp/sql.txt', 'w')
    file.write("select count(*) as total from ( "+ sqlthc + wherethc + " union "+ sqlses + whereses +")")
    file.close() 

#    consulta=cdb.executesql("select count(*) as total from thinclients where 1=1 "+wherethc)
    total = int(consulta[0][0])
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows }


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

