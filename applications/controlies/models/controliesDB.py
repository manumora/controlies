cdb = DAL('sqlite://controlies.sqlite')
cdb.define_table('laptops', 
                        Field('id_laptop','integer'),
                        Field('serial_number','string'),
                        Field('name','string'),
                        Field('mac_eth0','string'),
                        Field('mac_wlan0','string'),
                        Field('battery_sn','string'),
                        Field('charger_sn','string'),
                        Field('id_trademark','integer'),
                        primarykey=['id_laptop'])

cdb.define_table('laptops_trademarks', 
                        Field('id_trademark','integer'),
                        Field('trademark','string'),
                        Field('model','string'),
                        primarykey=['id_trademark'])

cdb.define_table('users_types', 
                        Field('id_user_type','integer'),
                        Field('user_type','string'),
                        primarykey=['id_user_type'])

try:
    cdb.users_types.insert(id_user_type='1',user_type='Profesor')
except:
    pass

try:
    cdb.users_types.insert(id_user_type='2',user_type='Alumno')
except:
    pass

cdb.define_table('laptops_historical', 
                        Field('id_historical','integer'),
                        Field('id_laptop','integer'),                        
                        Field('datetime','datetime'),
                        Field('username','string'),
                        Field('name','string'),
                        Field('id_user_type','integer'),
                        Field('nif','string'),
                        Field('comment','string'),
                        Field('id_state','integer'),
                        primarykey=['id_historical'])

cdb.define_table('states', 
                        Field('id_state','integer'),
                        Field('state','string'),                        
                        primarykey=['id_state'])
try:
    cdb.states.insert(id_state='1',state='Sin asignar')
except:
    pass

try:
    cdb.states.insert(id_state='2',state='Asignado')
except:
    pass

try:
    cdb.states.insert(id_state='3',state='En reparación')
except:
    pass

try:
    cdb.states.insert(id_state='4',state='Desaparecido')
except:
    pass

cdb.define_table('printers',
                 Field ('id_printer','integer'),
                 Field('id_printer_trademark','integer'),
                 Field('model','string'),
                 Field('location','string'),
                 primarykey=['id_printer'])

cdb.define_table('printers_trademarks',
                 Field('id_printers_trademark','integer'),
                 Field('trademark','string'),
                 primarykey=['id_printers_trademark'])
                 

import datetime
cdb.define_table('sesiones',
    Field('host'),
    Field('usuario'),
    Field('timelogin','datetime',default=datetime.datetime.today()),
    Field('timelogout','datetime'),
    Field('tipohost'))
cdb.executesql('CREATE INDEX IF NOT EXISTS idxseshost ON sesiones (host);')
cdb.executesql('CREATE INDEX IF NOT EXISTS idxsesusuario ON sesiones (usuario);')

cdb.define_table(
    'maquinas',
    Field('host'),
    Field('tipohost'),
    Field('ultimorefresco','datetime',default=datetime.datetime.today()),
    Field('ultimoarranque','datetime'),
    Field('ultimopkgsync','datetime'),
    Field('estadopaquetes'),
    Field('logpkgsync','upload',autodelete=True),
    Field('ultimopuppet','datetime'),
    Field('estadopuppet'),
    Field('logpuppet','upload', autodelete=True),
    Field('alert','integer', default=0) )
    
cdb.executesql('CREATE INDEX IF NOT EXISTS idxmaqhost ON maquinas (host);')
cdb.executesql('CREATE INDEX IF NOT EXISTS idxmaqtime ON maquinas (ultimorefresco);')
  
cdb.define_table(
    'thinclients',
    Field('host'),
    Field('time','datetime',default=datetime.datetime.today()),
    Field('raton'),   # 0->poweroff, 1->absent, 2->present
    Field('teclado') )
cdb.executesql('CREATE INDEX IF NOT EXISTS idxthctime ON thinclients (time DESC);')
cdb.executesql('CREATE INDEX IF NOT EXISTS idxthchost ON thinclients (host);')


cdb.define_table('config',
          Field('mail_server','string'),
          Field('mail_sender','string'),
          Field('mail_user','string'),
          Field('mail_password','password'),
          Field ('mail_receiver','string'),
          Field ('alert_teclado','integer'),
          Field ('alert_raton','integer'),
          Field ('alert_apagado','integer'),
          Field ('list_email','integer'))


cdb.define_table('logprinter',
          Field('time','datetime',default=datetime.datetime.today()),
          Field('impresora','string'),
          Field('jobid','integer'),
          Field('usuario','string'),
          Field('host','string'),
          Field('trabajo','string'),
          Field('paginas','integer'),
          Field('copias','integer'),
          Field('total','integer'),
          Field ('tamanio','integer'))
          
cdb.define_table('horarios',
          Field('inicio','time'),
          Field('fin','time'),
          Field('descripcion','string'))

                 

cdb.define_table('clases_puppet',
          Field('time','datetime',default=datetime.datetime.today()),
          Field('tipohost','string'),
          Field('clase','string'))

cdb.define_table('clases_puppet_host',
          Field('id_clase', 'integer'),
          Field('time','datetime',default=datetime.datetime.today()),
          Field('host','string'),
          Field('resultado','string'))          

                 
