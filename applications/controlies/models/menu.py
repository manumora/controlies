# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = 'ControlIES'
response.subtitle = 'Centros educativos de Extremadura'

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'manuito chischo jredrejo'
response.meta.description = 'Aplicación para la gestión de usuarios y máquinas en los centros educativos de Extremadura'
response.meta.keywords = 'ldap, rayuela, linex,extremadura, institutos,usuarios,máquinas, workstations,ltsp'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2010-2012'


##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]



response.menu+=[
    ('LDAP', False,None,[
            ('Usuarios', False, URL( 'usuarios', 'index' )),
            ('Grupos', False,URL( 'grupos', 'index' )),
            ('Servidores LTSP',False, URL( 'hosts', 'ltspservers' )),
            ('Workstations', False,URL( 'hosts', 'workstations' )),
            ('Portátiles Profesores', False,URL( 'hosts', 'laptops' )),            
            ('Equipos Alumnos', False,URL( 'thinclients', 'index' )),         
            #('Parámetros DHCP', False,URL( 'dhcpd', 'index' )),
            ]
   )]



response.menu+=[('Gestión', False, None,[            
            ('Equipos', False,URL( 'gestion', 'servidores_aula')),
            ('Chat', False,URL( 'gestion', 'chat')),
            ('Importación de Rayuela', False, URL( 'gestion', 'rayuela')),
#            ('Mantenimiento de LDAP', False, None,[
#                ('Limpieza de grupos', False, URL('check_ldap','index')),
#                ('Detección de uid o gid duplicados', False, URL( 'gestion', 'duplicados')),
#                ]),
#            ('Importación datos de Portátiles', False, URL( 'gestion', 'base_datos')),
            ('Configuración', False, URL( 'gestion', 'config')),
            ]
   )]


response.menu+=[('Base de Datos', False, None,[            
            ('Dispositivos', False, None, [            
                ('Listado', False,URL( 'laptops', 'index')),
                ('Portátiles por Grupo', False,URL( 'laptops_groups', 'index')),
                ('Marcas', False,URL( 'laptops_trademarks', 'index'))  
                ]),
            ('Seguimiento', False, None, [            
                ('Seguimiento Usuarios', False,URL( 'seguimiento', 'index')), 
                ('Seguimiento Maquinas', False,URL( 'maquinas', 'index')), 
                ('Seguimiento Thinclients', False, URL('maquinas', 'index_thinclients')),
                ('Seguimiento Impresión', False, URL('logprinter', 'index')),
                ('Seguimiento Aulas', False, URL('maquinas', 'index_aulas')),
                ('Seguimiento Tareas Puppet', False, URL('puppet', 'index'))
                
                ]),
            ]
   )]

response.menu+=[('Informes', False, None,[            
            ('Compromisos Portátiles', False,URL( 'reports', 'laptops')),
            ('Estadísticas', False,URL( 'stadistics', 'index')),
            #('Impresoras', False,URL( 'reports', 'printers')),
            #('Usuarios', False,URL( 'reports', 'users')),
            ]
   )]

response.menu+=[('Acerca de', False, 'javascript:showInfo()')]
