# -*- coding: utf-8 -*-

from applications.controlies.modules.Hosts import Hosts

def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
        
    return dict()


################## PUPPET  ####################


@service.json
@auth.requires_login()
def list():

    fields = ['id','clase','tipohost''time_aparicion']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
    
    
    sql= "select cp.id as id, clase, tipohost, cp.time as time_aparicion, "
    sql= sql + "(select count (cph.id) from clases_puppet_host cph where cp.id=cph.id_clase) as total, "
    sql= sql + "(select count (cph.id) from clases_puppet_host cph where cp.id=cph.id_clase and cph.resultado='ERROR') as error "
    sql= sql + "from clases_puppet cp";
    where=" where 1=1 "
     
    try:
       if str(request.vars['tipohost']) != "None":
             where = where+" and tipohost like '%"+str(request.vars['tipohost'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['clase']) != "None":
             where = where+" and clase like '%"+str(request.vars['clase'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['time_aparicion']) != "None":
             where = where+" and cp.time like '%"+str(request.vars['time_aparicion'])+"%'"
    except LookupError:
       pass
    
        
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   

    consulta=cdb.executesql(sql)    
    for reg in consulta:    
        row = {
                "id":reg[0],
                "cell":[reg[0],reg[1],reg[2],reg[3],reg[4],reg[5]],                
                "clase": reg[1],                
                "tipohost":reg[2],                
                "time_aparicion":reg[3],
                "total":reg[4],
                "error":reg[5]                
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from clases_puppet "+where)
    total = int(consulta[0][0])
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows } 


@service.json
@auth.requires_login()
def list_clase():

    fields = ['id','clase','host','time_aplicacion','resultado']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
    
    idclase=request.vars['id_clase']
            
    sql="select id, id_clase, host, time as time_aplicacion,resultado  from clases_puppet_host "    
    where=" where id_clase="+idclase
     
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['resultado']) != "None":
             where = where+" and resultado like '%"+str(request.vars['resultado'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['time_aplicacion']) != "None":
             where = where+" and time like '%"+str(request.vars['time_aplicacion'])+"%'"
    except LookupError:
       pass
    
        
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   
    
    consulta=cdb.executesql(sql)    
    for reg in consulta:    
        row = {
                "id":reg[0],
                "cell":[reg[2],reg[3],reg[4]],                
                "id_clase": reg[1],                
                "host":reg[2],                
                "time_aplicacion":reg[3],
                "resultado":reg[4]
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as total from clases_puppet_host "+where)
    total = int(consulta[0][0])
    pages = int(total/pagesize) + 1
    return { "page":page, "total":pages, "records":total, "rows":rows } 


def formatearFecha(fecha):
	return fecha[6:]+"-"+fecha[3:5]+"-"+fecha[0:2]    


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

