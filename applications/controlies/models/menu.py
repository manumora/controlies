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
            ('Portátiles', False,URL( 'hosts', 'laptops' )),            
            ('Clientes Ligeros', False,URL( 'thinclients', 'index' )),         
            #('Parámetros DHCP', False,URL( 'dhcpd', 'index' )),
            ]
   )]



response.menu+=[('Gestión', False, None,[            
            ('Servidores de Aula', False,URL( 'gestion', 'servidores_aula')),   
            ('Importación de Rayuela', False, URL( 'gestion', 'rayuela')),
            ('Mantenimiento de LDAP', False, None,[
                ('Limpieza de grupos', False, URL('check_ldap','index')),
                ('Detección de uid o gid duplicados', False, URL( 'gestion', 'duplicados')),
                ])
#            ('Importación datos de Portátiles', False, URL( 'gestion', 'base_datos')),
            ]
   )]


response.menu+=[('Base de Datos', False, None,[            
            ('Dispositivos', False, None, [            
                ('Listado', False,URL( 'laptops', 'index')),
                ('Portátiles por Grupo', False,URL( 'laptops_groups', 'index')),
                ('Marcas', False,URL( 'laptops_trademarks', 'index'))  
                ]),
            ]
   )]

response.menu+=[('Informes', False, None,[            
            ('Compromisos Portátiles', False,URL( 'reports', 'laptops')),
            #('Usuarios', False,URL( 'reports', 'users')),
            ]
   )]

response.menu+=[('Acerca de', False, 'javascript:showInfo()')]