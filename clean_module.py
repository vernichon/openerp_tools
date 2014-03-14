#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import xmlrpclib
from openerp_connection import openerp
from openerp_connection import openerp_db
from openerp_connection import module as module_object

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d", "--db", dest="db",default='fiefmgt',help="Nom de la base ")
parser.add_option("-U", "--user", dest="user",default='FadminT',help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd",default='TezorganF',help="mot de passe OpenERP")
parser.add_option("-u", "--userdb", dest="userdb",default='postgres',help="User de la base")
parser.add_option("-w", "--passwddb", dest="passwddb",default='SezorganP',help="mot de passe du user de la base")
parser.add_option("-H", "--host", dest="host",default='192.168.12.252',help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port",default='8069',help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole",default='http',help="protocole http/https")
parser.add_option("-m", "--module", dest="module",default="None",help="module a supprimer")
(options,args)= parser.parse_args()

(options,args)= parser.parse_args()
if options.user == 'terp':
    options.user = options.db[:1].upper()+'admin'+options.db[-1].upper()
    options.passwd = options.db[-1].upper()+'ezorgan'+options.db[:1].upper()
try:
    connect_db=openerp_db(options.protocole+'://',options.host,options.port)
    connection=openerp(options.protocole+'://',options.host,options.port,options.db,options.user,options.passwd)  
    module_exec = module_object(connection)
except Exception, e:
    print "Erreur de connection ",e
    sys.exit(1)
    
module_exec.update_list()
module_exec.clean_all()

module_ids = connection.search('ir.module.module',[('state','in',('uninstallable',))])
res=None
if options.module <> 'None':
    module_id = connection.search('ir.module.module',[('name','=',options.module)])
    if module_id:
        module_ids.append(module_id[0])
for module_id in connection.search('ir.module.module',[('installed_version',"=",None)]):
    if module_id:
        module_ids.append(module_id)
for module_id in connection.search('ir.module.module',[('latest_version',"=",None)]):
    if module_id:
        module_ids.append(module_id)
for module_id in connection.search('ir.module.module',[('name',"like",'c2c%'),('state','in',('to upgrade','installed'))]):
    if module_id:
        module_ids.append(module_id)
for module_id in connection.search('ir.module.module',[('latest_version',"like",'4%'),('state','=','uninstalled')]):
    if module_id:
        module_ids.append(module_id)
for module_id in connection.search('ir.module.module',[('name',"like",'multi_company%')]):
    if module_id:
        module_ids.append(module_id)

for module_id in module_ids:
    try:
        module=connection.read('ir.module.module',module_id)
    except:
        module = None
        pass
    if  module:
 
        if module['name'] == options.module and module['state'] == 'installed':
            module_exec.uninstall(module_id=module_id)
            module=connection.read('ir.module.module',module_id)
        if module['name'] and module['installed_version'] == '':
            #print "Suppression                   %s "%module['name'] 
            #print "State                        ",module['state']
            #print "module['installed_version']  ", module['installed_version']
            #print "module['latest_version']     ",module['latest_version']
            module_exec.remove(module_name = module['name'],module_id = module_id)
            module_ids.remove(module_id)

print "That's all folks!"
