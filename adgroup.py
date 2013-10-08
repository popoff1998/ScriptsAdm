# -*- coding: utf-8 -*-
"""
Este script comprueba cuantos alumnos no estan en el grupo UCOUSERS

La comprobacion es doble:
    - Que el usuario no tenga ningun grupo
    - Que el usuario tenga grupos pero ninguno sea ucousers
    
Por razones de rendimiento no se puede trabajar directamente con objetos user de AD
Hay que hacer una query solo con los atributos cuenta y memberof y despues trabajar
desde python con la lista que hemos generado
"""


from pyad import *
import datetime
import filetimes


print "Conectando a AD y recuperando grupo"
pyad.set_defaults(ldap_server="sunsrv.uco.es")
ucousers_group = pyad.from_cn('UCOCUSERS')


lista_usuarios = []
lista_nomiembros = []
q = pyad.adsearch.ADQuery()

print "Ejecutando query de Alumnos"
#hacemos una query recuperando el atributo cuenta y los grupos
q.execute_query(
    attributes = ["sAMAccountName","memberOf"],
    where_clause = "objectClass = 'Person'",
    base_dn = "OU=Alumnos, DC=uco, DC=es"
)

print "Generando lista de usuarios"
#Esto nos generara una lista de diccionarios con los dos atributos
for user in q.get_results():
    lista_usuarios.append(user)
print "Hay ",len(lista_usuarios)," alumnos"

print "Comprobando la membresia a UCOUSERS"
procesados = 0
isiterable = lambda obj: isinstance(obj, basestring) \
    or getattr(obj, '__iter__', False)
for user in lista_usuarios:
    es_miembro = False
    procesados = procesados + 1
    print "Procesados: ",procesados
    #Si memberOf no es iterable es que no tiene ningun grupo    
    if isiterable(user['memberOf']):
        #Para cada usuario miramos la lista de grupos    
        for group in user['memberOf']:
            #Vemos si el literal UCOUSERS esta en ese grupo
            if "UCOUSERS" in group:
                es_miembro = True
    if not es_miembro:        
        lista_nomiembros.append(user)

print "Hay ",len(lista_usuarios)," alumnos"
print "Hay ",len(lista_nomiembros)," alumnos que no están en ucousers"
print "La lista de usuarios es:"
for user in lista_nomiembros:
    pyad.ADObject.get_attribute()
    aduser=pyad.from_cn(user['sAMAccountName'])
    exp_date = aduser.get
    print user['sAMAccountName'],filetimes.filetime_to_dt(user['accountExpires'])
