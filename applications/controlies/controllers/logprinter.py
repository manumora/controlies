# coding: utf8

from applications.controlies.modules.Users import Users
from applications.controlies.modules.Utils import Utils
from math import floor
import gluon.contenttype
import cStringIO
from gluon.contrib.pyfpdf import FPDF, HTMLMixin

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
    page =  int(request.vars["page"])
    pagesize = int(request.vars["rows"])    
    offset = (page-1) * pagesize
    
    groupBy=""

    if(request.vars["groupBy"]=="without"):
        sql="select id,time,impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio from logprinter where 1=1"
        
    if(request.vars["groupBy"]=="print"):
        sql="select '' as id,'' as time,impresora,'' as jobid,'' as usuario,'' as host,'' as trabajo,'' as paginas,'' as copias, SUM(total) AS total,'' as tamanio from logprinter where 1=1"
        groupBy=" GROUP BY impresora"

    if(request.vars["groupBy"]=="user"):
        sql="select '' AS id, '' AS time, '' AS impresora, '' AS jobid, usuario, '' AS host, '' AS trabajo, '' AS paginas, '' AS copias, SUM(total) AS total, '' AS tamanio from logprinter where 1=1"
        groupBy=" GROUP BY usuario"

    if(request.vars["groupBy"]=="host"):
        sql="select '' AS id, '' AS time, '' AS impresora, '' AS jobid, '' AS usuario, host, '' AS trabajo, '' AS paginas, '' AS copias, SUM(total) AS total, '' AS tamanio from logprinter where 1=1"
        groupBy=" GROUP BY host"

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
    
    where=where+ " and time between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where + groupBy +" order by "+request.vars['sidx']+" "+request.vars['sord'] + " limit "+str(pagesize)+" offset "+str(offset)   

    consulta=cdb.executesql(sql)
    
    rows = []
    for reg in consulta:
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

    consulta=cdb.executesql("select id from logprinter where 1=1 "+where + groupBy)
    totalreg = len(consulta)   

    # grid parameters
    if totalreg > 0:
        totalPages = floor( totalreg / pagesize )
        module = totalreg % pagesize
        if module > 0:
            totalPages = totalPages+1
    else:
        totalPages = 0

    if page > totalPages:
        page = totalPages

    #select sum() devuelve null si hay 0 registros, select total() devuelve 0.
    
    sql="select total(total) as totalpag from logprinter where 1=1 "+where
#    file = open('/tmp/sql.txt', 'w')
#    file.write(sql)
#   file.close() 

    consulta=cdb.executesql(sql)
    totalpag= int(consulta[0][0])   
    
    return { "page":page, "total":totalPages, "records":totalreg, "rows":rows, "userdata": {"trabajo": "Total................", "total": totalpag }} 


    
@auth.requires_login()   
def export_csv():
        
    consulta=consultaInforme()
    #Montamos el csv a mano, ya que export_to_csv_file(stream) solo funciona con el objeto Rows y executesql devuelve una lista.
    doc="Id,Time,Impresora,Jobid,Usuario,Host,Nombre_Trabajo,Paginas,Copias,Total,Tamanio\n"
                
    for reg in consulta:
        doc = doc+str(reg[0]) +',"'+reg[1]+'","'+reg[2]+'",'+str(reg[3])+',"'+reg[4]+'","'+reg[5]+'","'+reg[6]+'",'+str(reg[7])+","+str(reg[8])+","+str(reg[9])+","+str(reg[10])+"\n"
       
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    #Pasamos el documento a utf-8, si no da error el codifirlo en base64
    doc=doc.encode("utf-8")
    doc64=embed64(data=doc,extension='application/csv')    
    #No podemos darle un nombre, las data uri estandar no incluyen el nombre del fichero, solo el formato y los datos.
    return 'document.location="%s";' % doc64 


@auth.requires_login()   
def export_pdf():
    
    
    title = "Informe de impresiones"
    
    head = THEAD(TR(TH("Fecha/Hora",_width="16%"), 
                    TH("Impresora",_width="17%"),
                    TH("Host",_width="10%"),
                    TH("Usuario",_width="10%"),
                    TH("Trabajo",_width="33%"),
                    TH("Pag",_width="4%"), 
                    TH("Cop",_width="4%"), 
                    TH("Total",_width="6%"),  
                    _bgcolor="#A0A0A0"))

   
    rowsTable = []
    i=0;
    
    rows=consultaInforme()
    
    for r in rows:
        
        col = i % 2 and "#F0F0F0" or "#FFFFFF"

        documento=r[6].encode("latin_1","replace")[:50]
                      
        rowsTable.append(TR(TD(r[1], _align="left"),
                       TD(r[2], _align="left", _style="font-size: 20px;"),
                       TD(r[5], _align="left"),
                       TD(r[4], _align="left"),
                       TD(documento, _align="left"),
                       TD(r[7], _align="center"),
                       TD(r[8], _align="center"),
                       TD(r[9], _align="center"),
                       _bgcolor=col, _style="font-size: 5px;"))                       
        #rowsTable.append(TR(eval(fields), _bgcolor=col))
        i+=1 

    body = TBODY(*rowsTable)
    table = TABLE(*[head, body], _border="1", _align="center", _width="100%")

    class MyFPDF(FPDF, HTMLMixin):
        
        def __init__(self):
            FPDF.__init__(self,'L')
        
        def header(self):
            self.set_font('Arial','B',15)
            self.cell(0,10, title ,1,0,'C')
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial','I',8)
            self.cell(0,10,"IES",0,0,'L')
            txt = 'Pag. %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'R')
                
    pdf=MyFPDF()    
    pdf.add_page()    
    
    pdf.write_html(str(XML(table, sanitize=False)))        

    response.headers['Content-Type']='application/pdf; charset=utf-8'    
    doc=pdf.output(dest='S')
    doc64=embed64(data=doc,extension='application/pdf')    
    return 'window.open("%s");' % doc64 


@auth.requires_login()   
def export_pdf_user():
    
    
    title = "Informe de impresiones por usuario"
    
    head = THEAD(TR(TH("Fecha/Hora",_width="15%"), 
                    TH("Impresora",_width="15%"),
                    TH("Host",_width="10%"),                    
                    TH("Trabajo",_width="32%"),
                    TH("Pag",_width="5%"), 
                    TH("Cop",_width="5%"), 
                    TH("Total",_width="8%"),  
                    _bgcolor="#A0A0A0"))

    tablas=[]
    rowsTable = []
    i=0;
    
    rows=consultaInforme('USER')
    usuario=""
    subtotal=0
    
    for r in rows:
        
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        if usuario!=r[4]:
            if usuario!="":                
                rowsTable.append(TR(TD("Total impresiones ", _align="right", _colspan="6"), TD(subtotal, _align="center"), _border="1", _bgcolor="#F0F0F0"))                
                body = TBODY(*rowsTable)
                table = TABLE(*[head, body], _border="1", _align="center", _width="100%")                
                tablas.append(table)
            usuario=r[4]
            subtotal=0
            rowsTable=[]            
            rowsTable.append(TR(TD("USUARIO: " +usuario, _align="left", _colspan="7" ), _border="1", _bgcolor="#F0F0F0"))            
            
                       
        documento=r[6].encode("latin_1","replace")[:50]
                                         
        rowsTable.append(TR(TD(r[1], _align="left"),
                       TD(r[2], _align="left"),
                       TD(r[5], _align="left"),
                       TD(documento, _align="left"),
                       TD(r[7], _align="center"),
                       TD(r[8], _align="center"),
                       TD(r[9], _align="center"),
                       _bgcolor=col))                       
        subtotal=subtotal+r[9]
        
        i+=1 
    
    if len(rowsTable)>0 :
        rowsTable.append(TR(TD("Total impresiones ", _align="right", _colspan="6"), TD(subtotal, _align="center"), _border="1", _bgcolor="#F0F0F0"))                
        body = TBODY(*rowsTable)
        table = TABLE(*[head, body], _border="1", _align="center", _width="100%")                
        tablas.append(table)
        
    contenido = DIV(*tablas, _width="100%", _align="center")

    class MyFPDF(FPDF, HTMLMixin):
        
        def __init__(self):
            FPDF.__init__(self,'L')
        
        def header(self):
            self.set_font('Arial','B',15)
            self.cell(0,10, title ,1,0,'C')
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial','I',8)
            self.cell(0,10,"IES",0,0,'L')
            txt = 'Pag. %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'R')
                
    pdf=MyFPDF()
    ##pdf.set_font("Arial",'I', size=8) No vale para nada, no formatea bien
    pdf.add_page()    
    pdf.write_html(str(XML(contenido, sanitize=False)))        

    response.headers['Content-Type']='application/pdf'
    doc=pdf.output(dest='S')
    doc64=embed64(data=doc,extension='application/pdf')    
    return 'window.open("%s");' % doc64 

   

def consultaInforme(orden='GRID'):
    
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
    
    sql="select id,time,impresora,jobid,usuario,host,trabajo,paginas,copias,total,tamanio from logprinter where 1=1"     
    where=where+ " and time between '"+fechaini+"' and date('"+fechafin+"','+24 hours')"
    sql = sql + where
    
    if orden=='GRID':
         sql = sql + " order by "+request.vars['sidx']+" "+request.vars['sord']    
    elif orden=="USER":
         sql = sql + " order by usuario asc"   
    else:
         pass
         
    consulta=cdb.executesql(sql)
    
    return consulta

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

