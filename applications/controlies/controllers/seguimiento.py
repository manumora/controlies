# coding: utf8

from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils
import datetime

def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
        
    return dict()

################## SEGUIMIENTO  ####################


@service.json
@auth.requires_login()
def list():

    fields = ['host','usuario','timelogin','timelogout','tipohost']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
        
    sql="select id,host,usuario,timelogin,timelogout,tipohost from sesiones where 1=1"
    where=""
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['usuario']) != "None":
             where = where+" and usuario like '%"+str(request.vars['usuario'])+"%'"
    except LookupError:
       pass
       
    try:
       if str(request.vars['timelogin']) != "None":
             where = where+" and timelogin like '%"+str(request.vars['timelogin'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['timelogout']) != "None":
             where = where+" and timelogout like '%"+str(request.vars['timelogout'])+"%'"
    except LookupError:
       pass          

    try:
       if str(request.vars['tipohost']) != "None":
             where = where+" and tipohost like '%"+str(request.vars['tipohost'])+"%'"
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
       
#Convertimos las fechas a formato interno de sqlite: AAAA-MM-DD       
    fechaini = formatearFecha(fechaini)
    fechafin = formatearFecha(fechafin)
    
    where=where+ " and timelogin between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)
        
    # ile = open('/tmp/sql.txt', 'w')
    #file.write(sql)
    #file.close()   
       
    consulta=cdb.executesql(sql)

    for reg in consulta:
        row = {
                "id":reg[0],
                "cell":[reg[1],reg[2],reg[3],reg[4],reg[5]],
                "host":reg[1],
                "usuario":reg[2],
                "timelogin":reg[3],
                "timelogout":reg[4],
                "tipohost":reg[5]
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from sesiones where 1=1 "+where)
    total = int(consulta[0][0])   
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows  } 

@service.json
@auth.requires_login()
def borrarsesiones():

    retorno="OK"
    
    fechainiborrado='01-01-2000'
    try:
       if len(str(request.vars['fechainiborrado'])) > 0 :
             fechainiborrado=str(request.vars['fechainiborrado'])             
    except LookupError:
       pass
        
    try:
       if len(str(request.vars['fechafinborrado'])) > 0 :
          fechafinborrado=str(request.vars['fechafinborrado'])
       else:
		   retorno="fechafin"
    except LookupError:
	   retorno="fechafin"

    if retorno=="OK":
      if validarFecha(fechafinborrado) and validarFecha(fechainiborrado):
          fechainiborrado = formatearFecha(fechainiborrado)
          fechafinborrado = formatearFecha(fechafinborrado)
          sql="delete from sesiones where timelogin between '"+fechainiborrado+"' and date('"+fechafinborrado+"','+24 hours')"           
          file = open('/tmp/sql.txt', 'w')
          file.write(sql)
          file.close()       
          try:
              cdb.executesql(sql)
              retorno="OK"
          except:
              retorno="fail"
      else:
          retorno="format"
              
    return dict(response=retorno)
    
    
def formatearFecha(fecha):
	return fecha[6:]+"-"+fecha[3:5]+"-"+fecha[0:2]    

def validarFecha(fecha):
   try:
      datetime.datetime.strptime(fecha,"%d-%m-%Y")
      retorno=True
   except ValueError as err:
      retorno=False
   
   return retorno
   
@service.json
def getUserData():

    l=conecta()
    u = Users(l,"","","","",request.vars['username'],"","","","")
    response = u.getUserData()
    l.close()
    return dict(response=response)

    
def form():
    return dict()
        
def formdelete():
    return dict()    

def usuarioshost():
		
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

