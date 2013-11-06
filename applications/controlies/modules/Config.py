from gluon.tools import Mail
import smtplib
import datetime

class Config(object):

    
    def __init__(self,db):

        self.DB=db
        self.mail_server = ""      
        self.mail_sender = ""
        self.mail_user = ""        
        self.mail_password = ""
        self.mail_receiver = ""
        self.alert_thinclient=False
        self.list_email=False           


    def loadConfig(self):

        fila=self.DB(self.DB.config).select().first()
        if fila==None:
           self.mail_server = ""      
           self.mail_sender = ""
           self.mail_user = ""        
           self.mail_password = ""
           self.mail_receiver = ""
           self.alert_thinclient=False
           self.list_email=False           
        else:
           self.mail_server = fila["mail_server"]
           self.mail_sender = fila["mail_sender"]
           self.mail_user = fila["mail_user"]
           self.mail_password = fila["mail_password"]
           self.mail_receiver = fila["mail_receiver"]
           self.alert_thinclient=fila["alert_thinclient"]
           self.list_email=fila["list_email"]

    def enviaMail(self, asunto, mensaje):
		
		if self.mail_server != None and self.mail_server != ""  :
			
			mail = Mail()

			mail.settings.server = self.mail_server
			mail.settings.sender = self.mail_sender
			mail.settings.login = self.mail_user +":"+self.mail_password

			if mail.send(self.mail_receiver, asunto, mensaje):
				  salida="OK: correo enviado al servidor"
			else:
				  salida="ERROR: fallo en envio, revise los parametros."
		else:
			salida="ERROR: no configurado correo."
		
		return salida

    def validaMail(self):
		
        if self.mail_server != None and self.mail_server != "" :
		   #Separa en servidor:puerto
           datosservidor=self.mail_server.split(":")		           
           try :
              server = smtplib.SMTP(datosservidor[0],datosservidor[1])
              server.ehlo()
              server.starttls()  
              server.login(self.mail_user,self.mail_password)
              server.close()
              return True
           except Exception:
              server.close()
              return False
        
        return False
		

    def getConfigData(self):
    
          dataUser = {
            "mail_server": self.mail_server,
            "mail_sender": self.mail_sender,
            "mail_user": self.mail_user,
            "mail_password": self.mail_password,
            "mail_receiver": self.mail_receiver,            
            "alert_thinclient": self.alert_thinclient,
            "list_email": self.list_email
          }
         
          return dataUser
         

    def saveConfig(self,m_server,m_sender,m_user,m_password,m_receiver,alert_thinclient,list_email):

		self.mail_server = m_server
		self.mail_sender = m_sender
		self.mail_user = m_user
		self.mail_password = m_password
		self.mail_receiver = m_receiver
		self.alert_thinclient = alert_thinclient
		self.list_email = list_email

		fila=self.DB(self.DB.config).select().first()
		if fila==None:
			self.DB.config.insert(mail_server=self.mail_server, mail_sender=self.mail_sender, mail_user=self.mail_user, mail_password=self.mail_password, mail_receiver=self.mail_receiver, alert_thinclient=self.alert_thinclient, list_email= self.list_email)
		else:
			fila.update_record(mail_server=self.mail_server, mail_sender=self.mail_sender, mail_user=self.mail_user, mail_password=self.mail_password, mail_receiver=self.mail_receiver, alert_thinclient=self.alert_thinclient, list_email= self.list_email)
	
    
    def sendListReport(self):
        
        if self.list_email and self.validaMail():
            
            ahora=datetime.datetime.today()
            
            sql="select id,host,tipohost,ultimorefresco,ultimoarranque,ultimopkgsync,estadopaquetes,ifnull(ultimopuppet,'SIN INFO'),ifnull(estadopuppet,'SIN INFO') from maquinas "
            where=" where (estadopaquetes='ERROR') or (estadopuppet='ERROR') order by host"
        
            #    file = open('/tmp/sql.txt', 'w')
            #    file.write(sql)
            #    file.close()   
            
            
            mensaje="<html><body><b>Listado de maquinas con problemas detectados ("+ahora.strftime("%d/%m/%Y %H:%M")+ "):</b> <br/><br/>"            
            mensaje=mensaje+"<table border='1'><tr  style='font-weight:bold'><td width='8%'>HOST</td><td width='8%'>TIPOHOST</td><td width='19%'>ULT.REFRE</td><td width='19%'>ULT.BOOT</td>"
            mensaje=mensaje+"<td width='19%'>ULT.PKGSY</td><td width='8%'>PAQUETES</td><td width='19%'>ULT.PUPP</td><td>PUPPET</td></tr>"
            consulta=self.DB.executesql(sql+where)            
            cont=0
            for reg in consulta:                
                mensaje=mensaje+"<tr><td>"+reg[1]+"</td><td>"+reg[2]+"</td><td>"+reg[3]+"</td><td>"+reg[4]+"</td><td>"+reg[5]+"</td>"+"</td><td>"+reg[6]+"</td>"                
                mensaje=mensaje+"<td>"+ reg[7] +"</td>"+"<td>"+reg[8]+"</td></tr>"
                cont=cont+1
                
                
            mensaje=mensaje+"</table>"    
            
            sql="select distinct host from thinclients"
            consulta=self.DB.executesql(sql)
            mensaje=mensaje+"<br/><b>Listado de thinclients con problemas:<b><br/><br/>"
            mensaje=mensaje+"<table border='1'><tr  style='font-weight:bold'><td>HOST</td><td>FECHA</td><td>TECLADO</td><td>RATON</td></tr>"
            
            for reg in consulta:
                host=reg[0]
                sqlultimo="select id,host,time,teclado,raton from thinclients where host='"+host+"' order by time desc limit 1"   
                sql="select id,host,time,teclado,raton from thinclients where host='"+host+"' and (raton<>'2' or teclado<>'2') order by time desc limit 1"
                consulta_ultimo=self.DB.executesql(sqlultimo) #devuelve el ultimo valor de ese thinclient en la fecha indicada
                consulta_host=self.DB.executesql(sql) #devuelve una tupla o ninguna con el ultimo valor de ese thinclient
                                                  #en ese estado de raton y teclado
                if len(consulta_host)==1 :
                    reg=consulta_host[0]
                    reg_ultimo=consulta_ultimo[0]
                    if reg[0]==reg_ultimo[0]  :
                        #Si el ultimo registro del thinclient en esa fecha coincide con el ultimo
                        #registro con ese estado de raton y teclado, se incluye en la lista                        
                        if reg[3]=="0":
                            mensaje=mensaje+"<tr><td>"+reg[1]+"</td><td>"+reg[2]+"</td><td colspan=2>Apagado</td></tr>"
                        else:
                            teclado="Conectado" if reg[3]=="2" else "Desconectado"
                            raton="Conectado" if reg[4]=="2" else "Desconectado"
                            mensaje=mensaje+"<tr><td>"+reg[1]+"</td><td>"+reg[2]+"</td><td>"+teclado+"</td><td>"+raton+"</td></tr>"
                        cont=cont+1
            mensaje=mensaje+"</table>"    
            
            if cont==0 :
                mensaje=mensaje+"<b>Enhorabuena, tienes el IES como una patena!!!.</b>"    
            
            mensaje=mensaje+"</body></html>"     
            
            
            self.enviaMail('Informe de Controlies '+ahora.strftime("%d/%m/%Y %H:%M"), mensaje)
