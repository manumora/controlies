class Config(object):

    
    def __init__(self,db):

        self.DB=db


    def loadConfig(self):

        fila=self.DB(self.DB.config).select().first()
        if fila==None:
           self.mail_server = ""      
           self.mail_sender = ""
           self.mail_user = ""        
           self.mail_password = ""
           self.mail_receiver = ""
        else:
           self.mail_server = fila["mail_server"]
           self.mail_sender = fila["mail_sender"]
           self.mail_user = fila["mail_user"]
           self.mail_password = fila["mail_password"]
           self.mail_receiver = fila["mail_receiver"]


    def getConfigData(self):
    
          dataUser = {
            "mail_server": self.mail_server,
            "mail_sender": self.mail_sender,
            "mail_user": self.mail_user,
            "mail_password": self.mail_password,
            "mail_receiver": self.mail_receiver            
          }
         
          return dataUser

    def saveConfig(self,m_server,m_sender,m_user,m_password,m_receiver):

        self.mail_server = m_server
        self.mail_sender = m_sender
        self.mail_user = m_user
        self.mail_password = m_password
        self.mail_receiver = m_receiver

        fila=self.DB(self.DB.config).select().first()
        if fila==None:
            self.DB.config.insert(mail_server=self.mail_server, mail_sender=self.mail_sender, mail_user=self.mail_user, mail_password=self.mail_password, mail_receiver=self.mail_receiver)
        else:
            fila.update_record(mail_server=self.mail_server, mail_sender=self.mail_sender, mail_user=self.mail_user, mail_password=self.mail_password, mail_receiver=self.mail_receiver)

