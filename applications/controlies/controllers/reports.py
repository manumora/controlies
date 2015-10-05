# coding: latin1

def laptops():
    if not auth.user:
        session.flash='Debe iniciar sesi�n'
        redirect(URL(c='default',f='index'))
    return dict()

def printers():
    if not auth.user:
        session.flash='Debe iniciar sesi�n'
        redirect(URL(c='default',f='index'))
    return dict()

def users():
    if not auth.user:
        session.flash='Debe iniciar sesi�n'
        redirect(URL(c='default',f='index'))
    return dict()

@service.json 
def getClassrooms():
    import applications.controlies.modules.Utils.LdapUtils as LdapUtils
    l=conecta()
    response = LdapUtils.getAllGroups(l)
    l.close()
    return response

@auth.requires_login()      
def report():
    
    if request.vars['id_user_type']=="1":
        rows = getDataTeachers(request.vars['search'])
    else:
        rows = getDataStudents(request.vars['classroom'])

    if len(rows)==0:
        return "noPeople"

    from gluon.contrib.pyfpdf import FPDF, HTMLMixin
        
    if request.vars["report_type"]=="compromisos":
        
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                #logo=os.path.join(request.env.web2py_path,"applications","controlies","static","logo_consejeria.jpg")
                #self.image(logo,145,4,60)
                #self.ln(80)
                pass          
                
            def footer(self):
                #self.set_y(-15)
                #self.set_font('Arial','I',8)
                #self.cell(0,10,"IES Sta Eulalia - M�rida".decode("utf8").encode("latin1"),0,0,'L')
                #self.cell(0,10,"Consejer�a de Educaci�n - Gobierno de Extremadura".decode("utf8").encode("latin1"),0,0,'R')
                pass
            
        pdf=MyFPDF()
    
        count = 0
        titulo = "Compromiso para el cuidado y mantenimiento del ordenador port�til"
        
        for r in rows:
    
            if request.vars['id_user_type']=="1":
                parrafo1 = "D/D�a <b>"+r['cn']+"</b>, profesor/a de este centro , recibe en el d�a de hoy, de la Direcci�n del Centro, el ordenador port�til <b>"+r['trademark']+"</b> n�mero de serie: <b>"+r['serial_number']+"</b>, comprometi�ndose a utilizarlo como herramienta did�ctica en los cursos pertenecientes al Proyecto Escuela 2.0."
                parrafo2 = "Asimismo, se compromete a devolver a esta Direcci�n dicho ordenador port�til en el momento en que deje de tener vinculaci�n laboral con este centro o no sea profesor de alg�n curso integrado en el citado Proyecto Escuela 2.0."        
                parrafo3 = "M�rida, a ...... de ....................... de ......"
                parrafo4 = "Firmado: ............................................."
            else:
                parrafo1 = "Yo <b>"+r["cn"]+"</b> alumno/a de este centro perteneciente al curso/grupo <b>"+request.vars['classroom']+"</b>, me comprometo a cuidar, custodiar y mantener en perfecto estado el ORDENADOR <b>"+r['trademark']+"</b> (n�mero de serie: <b>"+r['serial_number']+"</b>) y ACCESORIOS que me ha entregado el centro para su uso en las distintas �reas de conocimientos, con la supervisi�n de los profesores/as correspondientes y siguiendo siempre las indicaciones e instrucciones para su correcto manejo."
                parrafo2 = "El deteriodo intencionado, p�rdida, robo o cualquier otra circunstancia que se produzca en el equipo ser� valorado por al Direcci�n/Jefatura del centro para tomar las medidas oportunas para su esclarecimiento y en su caso la reposici�n o arreglo por cuenta del alumno/a asignado/a, padres o tutores del mismo."        
                parrafo3 = "M�rida, a ...... de ....................... de ......"
                parrafo4 = "Firma del alumno: ....................................                     Firma de los padres/tutores: ...................................."
            
            if count%2==0:
                pdf.add_page()
            else:
                pdf.write_html("<br><br><br><center><p>______________________________________________________________________________________</p></center><br><br>")
    
            pdf.write_html("<center><h1>"+titulo+"</h1></center><br>")
            pdf.write_html("<p>"+parrafo1+"</p><br>")
            pdf.write_html("<p>"+parrafo2+"</p>")
            pdf.write_html("<br><br><center><p>"+parrafo3+"</p></center>")
            pdf.write_html("<br><br><br><br><center><p>"+parrafo4+"</p></center>")
            
            count+=1            
    
    elif request.vars["report_type"]=="listado":

        title = "Listado de dispositivos"

        html = """<table with='100%'>
                    <thead>
                    <tr><th>sdffsd</th><th></th><th></th></tr>
                    </thead>
                    <tbody>
                    <tr><td>sdffsd</td><td></td><td></td></tr>
                    <tr><td>sdffsd</td><td></td><td></td></tr>
                    </tbody>
                    </table>"""

        head = THEAD(TR(TH("N�",_width="5%"),
                        TH("Nombre y apellidos",_width="30%"),
                        TH("Marca/Modelo",_width="22%"),
                        TH("N� Serie",_width="30%"),
                        TH("Estado",_width="13%"),
                        _bgcolor="#A0A0A0"))

        rowsTable = []
        i=0;
        for r in rows:
            col = i % 2 and "#F0F0F0" or "#FFFFFF"
            rowsTable.append(TR(TD(i+1),
                           TD(r["cn"]),
                           TD(r["trademark"], _align="center"),
                           TD(r["serial_number"], _align="center"),
                           TD(r["state"], _align="center"),
                           _bgcolor=col))
            i+=1 

        body = TBODY(*rowsTable)
        table = TABLE(*[head, body], _border="1", _align="center", _width="100%")

        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, title ,1,0,'C')
                self.set_font('Arial','I',10)
                
                if request.vars['id_user_type']=="1": # Para profesores
                    self.text(20,29, "Grupo: Profesores")                    
                else:
                    self.text(20,29, "Grupo: "+request.vars['classroom'])
                    
                self.ln(10)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                self.cell(0,10,"IES Sta Eulalia",0,0,'L')
                txt = 'P�gina %s de %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'R')
                    
        pdf=MyFPDF()
        pdf.add_page()
        pdf.write_html('<font size="9">' +table.xml() + '</font>')

    response.headers['Content-Type']='application/pdf'
    doc=pdf.output(dest='S')
    doc64=embed64(data=doc,extension='application/pdf')    
    #return 'document.location="%s";' % doc64     
    return 'window.open("%s");' % doc64

def getDataStudents(classroom):
    from applications.controlies.modules.Groups import Groups

    l=conecta()
    g = Groups(l,"",classroom,"")
    listUsers = g.listUsers({'rows':'40', 'page':'1', 'sidx':'cn', 'sord':'desc'})
    l.close()

    # Obtenemos los numeros de serie de los portatiles
    sql = "SELECT lh.username, l.serial_number, lt.trademark, lt.model, st.state FROM laptops l, laptops_historical lh"
    sql = sql+" LEFT JOIN laptops_trademarks lt ON l.id_trademark=lt.id_trademark"
    sql = sql+" LEFT JOIN states st ON st.id_state=lh.id_state "
    sql = sql+" WHERE lh.id_user_type=2 AND l.id_laptop=lh.id_laptop "
    sql = sql+" AND lh.id_historical IN (SELECT MAX(lh2.id_historical) FROM laptops_historical lh2 WHERE lh2.id_laptop=l.id_laptop) "
    sql = sql+" GROUP BY l.id_laptop ORDER BY lh.name asc"
    result = cdb.executesql(sql)
    serials={}
    for r in result:
        if str(r[0])!="":
            serials[str(r[0])]={'serial':str(r[1]), 'trademark':str(r[2])+' - '+str(r[3]), 'state':str(r[4].encode('utf-8'))}

    rows=[]
    for r in listUsers["rows"]:
        num=""
        trademark=""
        state=" "
        if r["cell"][1] in serials:
            num = serials[r["cell"][1]]['serial']
            trademark = serials[r["cell"][1]]['trademark']
            state = serials[r["cell"][1]]['state']

        if num=="":
            num = "                                              "

        if trademark=="":
            trademark = "                                         "

        r["cell"].append(num)
        r["serial_number"]=num
        r["cell"].append(trademark)
        r["trademark"]=trademark
        r["state"]=state
        rows.append(r)
        
    return rows

def getDataTeachers(search):
    sql = "SELECT lh.username, l.serial_number, lh.name, lt.trademark, lt.model, st.state "
    sql = sql+" FROM laptops l, laptops_historical lh"
    sql = sql+" LEFT JOIN laptops_trademarks lt ON l.id_trademark=lt.id_trademark "        
    sql = sql+" LEFT JOIN users_types ut ON ut.id_user_type=lh.id_user_type "
    sql = sql+" LEFT JOIN states st ON st.id_state=lh.id_state "
    sql = sql+" WHERE lh.id_user_type=1"
    sql = sql+" AND l.id_laptop=lh.id_laptop "
    sql = sql+" AND lh.id_historical IN (SELECT MAX(lh2.id_historical) FROM laptops_historical lh2 WHERE lh2.id_laptop=l.id_laptop) "
    
    if search!="":
        sql = sql+" AND (lh.username like '%"+search+"%' "
        sql = sql+" OR lh.name like '%"+search+"%' "
        sql = sql+" OR l.serial_number like '%"+search+"%' "
        sql = sql+" OR lt.trademark like '%"+search+"%' "
        sql = sql+" OR lt.model like '%"+search+"%')"
    
    sql = sql+" GROUP BY l.id_laptop ORDER BY lh.name asc"
    result = cdb.executesql(sql)

    serials={}
    teachers = []
    for r in result:
        if str(r[0])!="" and str(r[0])!="None":
            #serials[str(r[0])] = { 'serial_number':str(r[1].encode('latin1')), 'cn':str(r[2].encode('latin1')) , 'trademark':str(r[3].encode('latin1'))+' - '+str(r[4].encode('latin1')) }
            #serials.append({ 'serial_number':str(r[1].encode('latin1')), 'cn':str(r[2].encode('latin1')) , 'trademark':str(r[3].encode('latin1'))+' - '+str(r[4].encode('latin1')) })
            teachers.append({ 'serial_number':str(r[1].encode('latin1')), 'cn':str(r[2].encode('latin1')) , 'trademark':str(r[3].encode('latin1'))+' - '+str(r[4].encode('latin1')) , 'state':str(r[5].encode('latin1'))})

    return teachers
    """for s in serials:
        teachers.append(serials[s])
    return teachers"""


@auth.requires_login()      
def report_printers():
    from gluon.contrib.pyfpdf import FPDF, HTMLMixin
                
    title = "Informe de impresiones"
    
    head = THEAD(TR(TH("Fecha/Hora",_width="22%"), 
                    TH("Impresora",_width="22%"),
                    TH("Host",_width="19%"),
                    TH("Usuario",_width="19%"),
                    TH("P�g",_width="5%"), 
                    TH("Cop",_width="5%"), 
                    TH("Total",_width="8%"),  
                    _bgcolor="#A0A0A0"))

    totalsum = cdb.logprinter.total.sum().with_alias('totalsum')

    rows=cdb(cdb.logprinter).select(cdb.logprinter.time,
                                    cdb.logprinter.impresora,
                                    cdb.logprinter.host,
                                    cdb.logprinter.usuario,
                                    cdb.logprinter.paginas,
                                    cdb.logprinter.copias,
                                    totalsum,
                                    groupby=cdb.logprinter.usuario,
                                    orderby=~cdb.logprinter.total.sum())
    
    rowsTable = []
    i=0;
    
    fields = " TD(r['logprinter']['time'], _align='center'),"
    fields+= " TD(r['logprinter']['impresora'], _align='center'),"
    fields+= " TD(r['logprinter']['host'], _align='center'),"
    fields+= " TD(r['logprinter']['usuario'], _align='center'),"
    fields+= " TD(r['logprinter']['paginas'], _align='center'),"
    fields+= " TD(r['logprinter']['copias'], _align='center'),"
    fields+= " TD(r['totalsum'], _align='center')"
    
    for r in rows:
        print r
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        """rowsTable.append(TR(TD(r['logprinter']['time'], _align="center"),
                       TD(r['logprinter']['impresora'], _align="center"),
                       TD(r['logprinter']['host'], _align="center"),
                       TD(r['logprinter']['usuario'], _align="center"),
                       TD(r['logprinter']['paginas'], _align="center"),
                       TD(r['logprinter']['copias'], _align="center"),
                       TD(r['totalsum'], _align="center"),
                       _bgcolor=col))"""
        rowsTable.append(TR(eval(fields), _bgcolor=col))
        i+=1 

    body = TBODY(*rowsTable)
    table = TABLE(*[head, body], _border="1", _align="center", _width="100%")

    class MyFPDF(FPDF, HTMLMixin):
        def header(self):
            self.set_font('Arial','B',15)
            self.cell(0,10, title ,1,0,'C')
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial','I',8)
            self.cell(0,10,"IES Sta Eulalia",0,0,'L')
            txt = 'P�gina %s de %s' % (self.page_no(), self.alias_nb_pages())
            self.cell(0,10,txt,0,0,'R')
                
    pdf=MyFPDF()
    pdf.add_page()
    pdf.write_html(str(XML(table, sanitize=False)))        

    response.headers['Content-Type']='application/pdf'
    doc=pdf.output(dest='S')
    doc64=embed64(data=doc,extension='application/pdf')    
    return 'document.location="%s";' % doc64 


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
