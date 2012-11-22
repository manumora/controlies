#!/usr/bin/env python 
# -*- coding: utf-8 -*-
##############################################################################
# Project:     ControlIES
# Module:      Rayuela2Ldap.py
# Purpose:     Populate corporative ldap with data from Rayuela
# Language:    Python 2.5
# Date:        1-Jun-2011.
# Ver:         13-Jun-2011.
# Author:   José L. Redrejo Rodríguez
# Copyright:    2011 - José L. Redrejo Rodŕiguez <jredrejo @no-spam@ debian.org>
#
#
# ControlIES is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ControlIES is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with ControlIES. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import Image #añadi
from gluon.storage import Storage
import xml.dom.minidom
import StringIO
import ldap
from Users import Users
from Groups import Groups
import Utils.LdapUtils as LdapUtils
import zipfile, cStringIO

class Rayuela(object):

    def __init__(self,conexion,archivo,borrar):
        self.borrando=borrar
        self.esAlumnos=False
        self.ldap_con =conexion
        self.usuarios=[]
        self.dni_usuarios=[]
        self.logins=[]
        self.archivo=archivo

    def getzip(self, filename, ignoreable=100):
        try:        
            return zipfile.ZipFile(filename)
        except zipfile.BadZipfile:
            original = open(filename, 'rb')
            try:
                data = original.read()
            finally:
                original.close()

            position = data.rindex(zipfile.stringEndArchive, -(22 + ignoreable), -20)
            coredata = cStringIO.StringIO(data[: 22 + position])
            return zipfile.ZipFile(coredata)

    def unzip_alumnos(self,archivo_zip):
        """ Descomprime el archivo de alumnos en el directorio
        /tmp/rayuela-ldap"""
        try:
            myzip = self.getzip(archivo_zip)
            myzip.extractall(path="/tmp/rayuela-ldap")
        except Exception,e:
            return e
            
        if not os.path.exists("/tmp/rayuela-ldap/Alumnos.xml"):
            return "No es un archivo de importación de alumnos"
            
        return "" #todo ha ido bien

    
    def asegura_codigos(self,cadena):
        """Quita caracteres no válidos para los nombres de login
        de los usuarios"""
        resultado = cadena.replace(u"á", u"a")
        resultado = resultado.replace(u"Á", u"A")
        resultado = resultado.replace(u"à", u"a")
        resultado = resultado.replace(u"ä", u"a")
        resultado = resultado.replace(u"À", u"A")
        resultado = resultado.replace(u"Ä", u"A")        
        resultado = resultado.replace(u"é", u"e")
        resultado = resultado.replace(u"ë", u"e")        
        resultado = resultado.replace(u"É", u"E")
        resultado = resultado.replace(u"Ë", u"E")        
        resultado = resultado.replace(u"è", u"e")
        resultado = resultado.replace(u"È", u"E")
        resultado = resultado.replace(u"í", u"i")
        resultado = resultado.replace(u"Í", u"I")
        resultado = resultado.replace(u"ì", u"i")
        resultado = resultado.replace(u"ï", u"i")        
        resultado = resultado.replace(u"Ì", u"I")
        resultado = resultado.replace(u"Ï", u"I")        
        resultado = resultado.replace(u"ó", u"o")
        resultado = resultado.replace(u"Ó", u"O")
        resultado = resultado.replace(u"Ö", u"O")
        resultado = resultado.replace(u"ò", u"o")
        resultado = resultado.replace(u"ö", u"o")        
        resultado = resultado.replace(u"Ò", u"O")
        resultado = resultado.replace(u"ú", u"u")
        resultado = resultado.replace(u"Ú", u"U")
        resultado = resultado.replace(u"ü", u"u")
        resultado = resultado.replace(u"Ü", u"U")
        resultado = resultado.replace(u"ù", u"u")
        resultado = resultado.replace(u"Ù", u"U")
        resultado = resultado.replace(u"ª", u"a")
        resultado = resultado.replace(u"º", u"o")
        resultado = resultado.replace(u"ñ", u"n")
        resultado = resultado.replace(u"Ñ", u"N")
        resultado = resultado.replace(u"ç", u"c")
        resultado = resultado.replace(u"(", u"")
        resultado = resultado.replace(u")", u"")    
        resultado = resultado.replace(u".", u"")
        resultado = resultado.replace(u",", u"")  
        resultado = resultado.replace(u"&", u"")
        return str(resultado).strip()


    def chk_username(self,login,keep=False):
        """Comprueba si el login existe ya en la base de datos
        de ldap, y si existe le va aumentando el número del final"""
        if not keep:
			nuevo_login= login + "01"
        else:
			nuevo_login=login
        result = self.ldap_con.search("ou=People","uid="+ nuevo_login,["uid"])

        if len(result)==0 and nuevo_login not in self.logins:
            return nuevo_login
        else:
            i=2
            while len(result)>0 or nuevo_login in self.logins:
                nuevo_login=login + "%02d" % (i)
                result = self.ldap_con.search("ou=People","uid="+ nuevo_login,["uid"])
                i += 1
            return nuevo_login

    def crea_logins(self):
        """Revisa la lista de usuarios y le asigna nuevo login al que
        no está ya en ldap o no lo trae de Rayuela"""

        for usuario in self.usuarios:
            usuario["nuevo"]=True
            if "dni" in usuario.keys():
                #contraseña del usuario:
                if self.esAlumnos:
                    usuario["passwd"]=usuario["fecha-nacimiento"].replace("/","")
                    if usuario["passwd"]=="": usuario["passwd"]=usuario["dni"]
                else:
                    usuario["passwd"]=usuario["dni"]            
                
                #login del usuario, primero vemos si ya está en ldap:
                result = self.ldap_con.search("ou=People","employeeNumber="+ usuario["dni"],["uid"])
                if len(result) > 0:
                    usuario["login"]=result[0][0][1]['uid'][0]
                    usuario["nuevo"]=False
                    
                else: #si el usuario no está en ldap y es nuevo, hay que crearle el login
                    if  usuario["datos-usuario-rayuela"] != "false": #esta en rayuela  su login
                        # en Rayuela no están validando los logins, lo que provoca que pueda haber
                        # logins no validos. Así que nos toca hacerlo a nosotros:
                        login_rayuela=self.asegura_codigos(usuario["datos-usuario-rayuela"])
                        login_rayuela=login_rayuela.lower().replace("-","").replace(" ","")
                        usuario["login"]=self.chk_username(login_rayuela,True)
                        
                    else: #iniciales del nombre + primer apellido + inicial segundo apellido
                        login=''              
                        for i in zip(*usuario["nombre"].lower().split(" "))[0]:
                            login += i.strip()
                        for i in usuario["primer-apellido"].lower().replace("-"," ").split(" "):
                            login += i.strip()
                        if "segundo-apellido" in usuario.keys():
                            if len(usuario["segundo-apellido"])>0:
                                login += usuario["segundo-apellido"][0].lower().strip()
                        usuario["login"]=self.chk_username(login)
                self.logins.append(usuario["login"])                   
            
            else: #sin nie ni dni, no podemos gestionarlo
                self.usuarios.remove(usuario)

            
    def encode(self,grafico):
        """Convierte la foto del alumno a un tamaño pequeño y 
        en un formato gráfico aceptable en ldap"""
        archivo=os.path.join("/tmp/rayuela-ldap/",grafico)
        try:
            im = Image.open(archivo)
            im.thumbnail((60,80), Image.ANTIALIAS)
            if im.mode != "RGB":
                im = im.convert("RGB")
            buf= StringIO.StringIO()
            try:
                im.save(buf, format= 'JPEG')
                resultado=buf.getvalue()
            except Exception,e:
                return None
        except:
            return None
        return  resultado
    

    def parse_nodo(self,nodo):
        """ para cada nodo en el xml, obtiene sus datos y prepara sus grupos"""
        usuario={}

        for info in nodo.childNodes:        
            if info.nodeType!=info.TEXT_NODE:
                if info.nodeName in ("datos-usuario-rayuela","foto","grupos"):

                    dato=info.childNodes[1].firstChild.nodeValue
                    if info.nodeName=="foto" and dato=="true":
                        dato=info.getElementsByTagName("nombre-fichero")[0].firstChild.nodeValue
                    if info.nodeName=="datos-usuario-rayuela" and dato=="true":
                        dato=info.getElementsByTagName("login")[0].firstChild.nodeValue                
                    
                else:
                    try:
                        dato=info.firstChild.nodeValue                    
                    except : # no hay dato en este nodo, p. ej. segundo-apellido
                        dato=' '            
                if info.nodeName == 'nie':
                    usuario["dni"]=self.asegura_codigos(dato)
                elif info.nodeName == 'foto': #no paso asegura_codigos para no quitar el "."
                    usuario['foto']=str(dato)
                elif info.nodeName == 'grupo': #no paso asegura_codigos para no quitar el "."
                    nombre_grupo=self.asegura_codigos(dato).replace(" ","") 
                    if len(nombre_grupo)>0:
                        usuario['grupo']=nombre_grupo 
                                       
                else:
                    usuario[info.nodeName]=self.asegura_codigos(dato)
        
        self.usuarios.append(usuario)
        self.dni_usuarios.append(usuario["dni"])

    
    def parsea_archivo(self,archivo_xml,tipo):
        """Recorre el archivo xml y va generando la lista de usuarios"""
        
        xml_usuarios=xml.dom.minidom.parse(archivo_xml)
        lista= xml_usuarios.getElementsByTagName(tipo)
        
        for nodo in lista:
            self.parse_nodo(nodo)

        self.crea_logins()
    

    def lista_grupos(self,lista,clave,sin_grupo="SIN_AULA"):
        """Devuelve una enumeración de los grupos que pertenecen a 
        clave, siendo normalmente clave igual a aulas o dptos"""
        grupos={}
        
        for i in lista:
            if clave not in i.keys():
                grupo=sin_grupo
            else:
                grupo=i[clave]
                
            if grupo not in grupos.keys():
                grupos[grupo]=[i["login"]]
            else:
                grupos[grupo].append(i["login"])
                
        return grupos
            
            
    def crea_grupos(self,listado):
        """Da de alta en ldap los grupos de alumnos"""
        for grupo in listado:

            nuevo=Groups(self.ldap_con ,"school_class",str(grupo),"")       
            nuevo.add()
    
    def existsUsername(self,login):
        """comprueba si login existe ya en la bb.dd de ldap"""
        result = self.ldap_con.search("ou=People","uid="+ login,["uid"])
        if len(result) > 0:
            return True
        else:
            return False


    def crea_usuarios(self):
        """Da de alta en ldap los usuarios que están en el listado""" 
        lista=[]
        if self.esAlumnos:
            tipo="student"
        else:
            tipo="teacher"

        for usuario in self.usuarios:

            if not self.existsUsername(usuario['login']):
                if self.esAlumnos:
                    if usuario['foto'] == 'false':
                        foto=None
                    else:
                        foto=self.encode(usuario['foto'])
                else:
                    foto=None
                surname=usuario['primer-apellido'] + ' ' + usuario['segundo-apellido']    
                nuevo=Users(self.ldap_con ,tipo,usuario['nombre'],surname.strip(),
                    usuario['dni'],usuario['login'],usuario['passwd'],usuario['passwd'],'','',foto)
                nuevo.add()
                lista.append((usuario['login'],True,usuario['passwd']))
            else:
                lista.append((usuario['login'],False,''))
                
        return lista
        

    def rellena_students(self):
        """Da de alta en el grupo students los que están en listado"""
        if len(self.ldap_con.search("ou=Group","cn=students",["cn"]))==0:
            attr = [
            ('objectclass', ['top','posixGroup','lisGroup','lisAclGroup']),
            ('grouptype', ["authority_group"] ),		
            ('gidnumber', ["1100"] ),		
            ('cn', ['students'] ),
            ('description', ['Lista de estudiantes del centro']),
            ('memberuid', ['']),
            ('member', [''])
            ]
            self.ldap_con.add("cn=students,ou=Group", attr)  

                  
        for usuario in self.usuarios:
            attr=[(ldap.MOD_ADD, 'member', ['uid=' + usuario['login'] + ',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
            (ldap.MOD_ADD, 'memberUid', [usuario['login']] )]
            try:
                self.ldap_con.modify('cn=students,ou=Group', attr)
            except Exception,e:
                print e
        

    def rellena_teachers(self):
        """Da de alta en el grupo teachers a todos los que están en el listado"""
        if len(self.ldap_con.search("ou=Group","cn=teachers",["cn"]))==0:
            attr = [
            ('objectclass', ['top','posixGroup','lisGroup','lisAclGroup']),
            ('grouptype', ["authority_group"] ),		
            ('gidnumber', ["3000"] ),		
            ('cn', ['teachers'] ),
            ('description', ['Lista de profesores del centro']),
            ('memberuid', ['']),
            ('member', [''])
            ]
            self.ldap_con.add("cn=teachers,ou=Group", attr)  

                     
        for usuario in self.usuarios:
            attr=[(ldap.MOD_ADD, 'member', ['uid=' + usuario['login'] + ',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
                (ldap.MOD_ADD, 'memberUid', [usuario['login']] )]
            try:
                self.ldap_con.modify('cn=teachers,ou=Group', attr)
            except Exception,e:
                print e            


    def usuarios_grupos(self,lista_grupos):
        """Da de alta en cada grupo a los usuarios correspondientes"""

        for grupo in lista_grupos:
            for usuario in lista_grupos[grupo]:
                attr=[(ldap.MOD_ADD, 'member', ['uid=' + usuario + ',ou=People,dc=instituto,dc=extremadura,dc=es'] ),
                    (ldap.MOD_ADD, 'memberUid', [usuario] ) ]
                try:
                    self.ldap_con.modify('cn=' + grupo + ',ou=Group', attr)
                except Exception,e:
                    print e 


    def lista_antiguos(self,grupo):
        """Devuelve el listado de los dni de los usuarios que ya estaban en ldap antes"""
        lista={}
        home="/home/" + grupo
        comparar=home[:13]

        #resultado=self.ldap_con.search("ou=Group","cn=" + grupo ,["memberuid"])
        resultado=self.ldap_con.search("ou=People","objectClass=person" , ["employeeNumber","uid","homeDirectory"])
        miembros=[]
        for i in resultado:
            if i[0][1]['homeDirectory'][0][:13]==comparar: miembros.append(i)

        if len(miembros) > 0:
            for dato in miembros:
                if len(dato) > 0:
                    try:
                        dni=dato[0][1]['employeeNumber'][0]
                        uid=dato[0][1]['uid'][0]                 
                        lista[dni]=uid
                    except:
                        continue
            
        return lista


    def borra_antiguos(self,viejos):
        """Borra de la base de datos de ldap a los usuarios que estaban 
        en la lista de viejos y no están en la de nuevos"""
        borrables={}

        for usuario in viejos:
            if not usuario in self.dni_usuarios:
                borrables[usuario]=viejos[usuario]
                            
        for viejo in borrables:
            try:
                self.ldap_con.delete('uid='+ borrables[viejo] +',ou=People')
                self.ldap_con.delete("cn="+ borrables[viejo] +",ou=Group")
            except:
                pass #algún dato ya estaba borrado

    
    def gestiona_archivo(self):
        """Función principal que a partir del archivo hace todo en ldap"""
        
        aulas={}
        dptos={}
        
        self.esAlumnos=(self.archivo[-4:].lower()==".zip")
        
        if self.esAlumnos:
            intento=self.unzip_alumnos(self.archivo)
            if intento!="": 
                print "PROBLEMAS",intento
            else:
                usuarios_antiguos=self.lista_antiguos("alumnos")
                self.parsea_archivo("/tmp/rayuela-ldap/Alumnos.xml","alumno")
                aulas=self.lista_grupos(self.usuarios,"grupo")
        else:
            usuarios_antiguos=self.lista_antiguos("profesor")
            self.parsea_archivo(self.archivo,"profesor")
            dptos=self.lista_grupos(self.usuarios,"departamento","SIN_DPTO")
            
        self.crea_grupos(aulas)  
        self.crea_grupos(dptos)
        total=self.crea_usuarios()
        
        if self.esAlumnos:
            
         
            if self.borrando: LdapUtils.clean_students(self.ldap_con )   
            self.rellena_students()    
            self.usuarios_grupos(aulas)
        else:
            
            if self.borrando: LdapUtils.clean_teachers(self.ldap_con )
            self.rellena_teachers()
            self.usuarios_grupos(dptos)

        if self.borrando:
            self.borra_antiguos(usuarios_antiguos) 
                  
        return total
    
    
    
    
if __name__ == '__main__':    
    #El código siguiente es sólo para depuración y desarrollo
    #No tiene sentido fuera de ese contexto  
    import LdapConnection    
    session=Storage()
    session.server="ldap"
    session.username="admin"
    session.password="linex2008"
    
    ldap_con = LdapConnection.LdapConnection(session)
    ldap_con.process()    
    try:
        os.mkdir( "/tmp/rayuela-ldap")
    except:
        pass #problema de permisos o directorio ya creado
        
    archivo="/opt/instituto/santaeulalia/ExportacionDatosAlumnado.zip"
    archivo="/tmp/ExportacionDatosAlumnado.zip"
    
    rayuela=Rayuela(ldap_con,archivo,True)
    todos=rayuela.gestiona_archivo()
    
    LdapUtils.sanea_grupos(ldap_con)
    
    print todos
    
