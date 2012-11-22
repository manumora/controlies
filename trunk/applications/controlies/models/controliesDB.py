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