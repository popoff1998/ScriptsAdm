# -*- coding: utf-8 -*-
"""
Created on Tue Oct 08 08:35:23 2013

@author: tonin
"""

from pyad import *
import os
import cx_Oracle

ORACLE_SERVER='ibmblade47/av10g'
METHOD = "SIGU"
QUERY_NT = "SELECT * FROM UT_CUENTAS_NT"

lista_usuarios = []
lista_nohomecifs = []

lista_nocifshome = []
lista_otrohome = []
lista_nohome = []
lista_noexist = []


if METHOD == "AD":
    print "Conectando a AD y recuperando Personas"
    pyad.set_defaults(ldap_server="sunsrv.uco.es")
    
    q = pyad.adsearch.ADQuery()
    
    print "Ejecutando query de Personas"
    #hacemos una query recuperando el atributo cuenta y los grupos
    q.execute_query(
        attributes = ["sAMAccountName"],
        where_clause = "objectClass = 'Person'",
        base_dn = " DC=uco, DC=es"
    )
    
    print "Generando lista de personas"
    #Esto nos generara una lista de diccionarios con los dos atributos
    for user in q.get_results():
        lista_usuarios.append(user['sAMAccountName'])
    print "Hay ",len(lista_usuarios)," personas en AD"

if METHOD == "SIGU":
    ORACLE_PASS = raw_input('     Introduzca la clave de oracle (sigu): ')
    print "Conectando a Sigu"
    try:
        oracleCon = cx_Oracle.connect('sigu/'+ORACLE_PASS+'@'+ORACLE_SERVER)
        print "CORRECTO"
    except:
        print "ERROR conectando a sigu"
        exit(False)

    print "Recuperando usuarios de sigu"
    try:
        cursor = oracleCon.cursor()
        cursor.execute(QUERY_NT)     
        tmpList = cursor.fetchall()
        cursor.close()
    except BaseException,e:
        print "ERROR: Error recuperando la lista de usuarios NT de sigu"
        exit(False)
    lista_usuarios = [x[0] for x in tmpList]     
    print "Hay ",len(lista_usuarios)," personas en sigu"
    
print "Comprobando si tienen home"
procesados = 0

for user in lista_usuarios:
    procesados = procesados + 1
    if not (procesados % 10000): print "Procesados: ",procesados
    home = "\\\\cifs\\homescif$\\"+user
    if os.path.exists(home):       
        pass
    else:
        lista_nohomecifs.append(user)
        
print "Hay ",len(lista_usuarios)," personas"
print "Hay ",len(lista_nohomecifs)," personas que no tienen home en homescif"

print "Comprobando homes alternativos"
for user in lista_nohomecifs:
    aduser=pyad.from_cn(user)
    try:
        home = aduser.get_attribute("HomeDirectory")
        if u'\\\\CIFS\\HOME' in home:
            lista_nocifshome.append(user)            
        elif home == []:
            lista_nohome.append(user)
        else:
            lista_otrohome.append(user)
    except:
            lista_noexist.append(user)
        
print "Resumen de resultados"
print "Usuarios que no existen: ",len(lista_noexist)
print "Usuarios con home distinto de homescif: ",len(lista_otrohome)
print "Usuarios sin home definido: ",len(lista_nohome)
print "Usuarios con home en homescif pero que no existe: ",len(lista_nocifshome)
print "Usuarios con home en homescif y que si lo tienen: ",len(lista_usuarios)-len(lista_nohomecifs)

print "Guardando las listas de usuarios"

f = open("usuarios_sin_home.txt","w")
f.write('\n'.join(lista_nohome))
f.close()

f = open("usuarios_no_existen.txt","w")
f.write('\n'.join(lista_noexist))
f.close()

f = open("usuarios_home_distinto_homescif.txt","w")
f.write('\n'.join(lista_otrohome))
f.close()

f = open("usuarios_homescifs_nocreado.txt","w")
f.write('\n'.join(lista_nocifshome))
f.close()
