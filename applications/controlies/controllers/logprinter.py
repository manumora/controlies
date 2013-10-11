# coding: utf8

from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils
import gluon.contenttype
import cStringIO

def index():
    if not auth.user:
        session.flash='Debe iniciar sesión'
        redirect(URL(c='default'))
        
    return dict()



################## SEGUIMIENTO  ####################


@service.json
@auth.requires_login()
def list():

       
    fields = ['time','impresora','jobid','usuario','host','trabajo','paginas','copias','total','tamanio']
    rows = []
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
            
    sql="select id,time,impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio from logprinter where 1=1"
    where=""
    
    
    try:
       if str(request.vars['time']) != "None":
             where = where+" and time like '%"+str(request.vars['time'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['impresora']) != "None":
             where = where+" and impresora like '%"+str(request.vars['impresora'])+"%'"
    except LookupError:
       pass
        
    try:
       if str(request.vars['jobid']) != "None":
             where = where+" and jobid>="+str(request.vars['jobid'])+" "
    except LookupError:
       pass
       
    try:
       if str(request.vars['usuario']) != "None":
             where = where+" and usuario like '%"+str(request.vars['usuario'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['trabajo']) != "None":
             where = where+" and trabajo like '%"+str(request.vars['trabajo'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['paginas']) != "None":
             where = where+" and paginas>="+str(request.vars['paginas'])+" "
    except LookupError:
       pass          

    try:
       if str(request.vars['copias']) != "None":
             where = where+" and copias>="+str(request.vars['copias'])+" "
    except LookupError:
       pass

    try:
       if str(request.vars['total']) != "None":
             where = where+" and total>="+str(request.vars['total'])+" "
    except LookupError:
       pass

    try:
       if str(request.vars['tamanio']) != "None":
             where = where+" and tamanio>="+str(request.vars['tamanio'])+" "
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
    
    where=where+ " and time between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   
    
 #   file = open('/tmp/sql.txt', 'w')
 #   file.write(sql)
 #   file.close()   

    consulta=cdb.executesql(sql)
    retorno=""
    for reg in consulta:
        retorno=retorno+reg[1]
        row = {
                "id":reg[0],
                "cell":[reg[1],reg[2],reg[3],reg[4],reg[5],reg[6],reg[7],reg[8],reg[9],reg[10]],
                "time":reg[1],
                "impresora": reg[2],
                "jobid":reg[3],
                "usuario":reg[4],
                "host":reg[5],
                "trabajo":reg[6],
                "paginas":reg[7],
                "copias":reg[8],
                "total":reg[9],
                "tamanio":reg[10],
            }
        rows.append(row)

    consulta=cdb.executesql("select count(*) as numregistros from logprinter where 1=1 "+where)
    totalreg = int(consulta[0][0])   
    pages = int(totalreg/pagesize) + 1
    
    consulta=cdb.executesql("select sum(total) as totalpag from logprinter where 1=1 "+where)
    totalpag= int(consulta[0][0])   
    
    return { "page":page, "total":pages, "records":totalreg, "rows":rows, "userdata": {"trabajo": "Total................", "total": totalpag }} 
    
    
@service.run
@auth.requires_login()   
def export_csv():
	
    response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
    
    stream=cStringIO.StringIO()
    
      
    consulta=cdb(cdb.logprinter).select()
    consulta.export_to_csv_file(stream)
       
    response.headers['Content-disposition'] = 'attachment; filename=%s.csv' % 'logimpresion'
    response.write(stream.getvalue())
    
    return stream.getvalue()

def list_all():    
      
    fields = ['time','impresora','jobid','usuario','host','trabajo','paginas','copias','total','tamanio']
    rows = []
            
    sql="select id,time,impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio from logprinter where 1=1"
    where=""
    
    
    try:
       if str(request.vars['time']) != "None":
             where = where+" and time like '%"+str(request.vars['time'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['host']) != "None":
             where = where+" and host like '%"+str(request.vars['host'])+"%'"
    except LookupError:
       pass
    
    try:
       if str(request.vars['impresora']) != "None":
             where = where+" and impresora like '%"+str(request.vars['impresora'])+"%'"
    except LookupError:
       pass
        
    try:
       if str(request.vars['jobid']) != "None":
             where = where+" and jobid>="+str(request.vars['jobid'])+" "
    except LookupError:
       pass
       
    try:
       if str(request.vars['usuario']) != "None":
             where = where+" and usuario like '%"+str(request.vars['usuario'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['trabajo']) != "None":
             where = where+" and trabajo like '%"+str(request.vars['trabajo'])+"%'"
    except LookupError:
       pass
   
    try:
       if str(request.vars['paginas']) != "None":
             where = where+" and paginas>="+str(request.vars['paginas'])+" "
    except LookupError:
       pass          

    try:
       if str(request.vars['copias']) != "None":
             where = where+" and copias>="+str(request.vars['copias'])+" "
    except LookupError:
       pass

    try:
       if str(request.vars['total']) != "None":
             where = where+" and total>="+str(request.vars['total'])+" "
    except LookupError:
       pass

    try:
       if str(request.vars['tamanio']) != "None":
             where = where+" and tamanio>="+str(request.vars['tamanio'])+" "
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
    
    where=where+ " and time between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where+" order by "+request.vars['sidx']+" "+request.vars['sord'] 
     
    consulta=cdb.executesql(sql)
    
    return consulta
    

def formatearFecha(fecha):
	return fecha[6:]+"-"+fecha[3:5]+"-"+fecha[0:2]    


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

