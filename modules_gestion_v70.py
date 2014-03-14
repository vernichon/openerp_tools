#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys
from openerp_connectionv7 import openerp
from openerp_connectionv7 import openerp_db
from openerp_connectionv7 import module
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-f", "--force", dest="force",default=None,help="Force update")
parser.add_option("-a", "--action", dest="action",default='update_list',help="Action install, update, update_all,update_list, remove, versioncourante")
parser.add_option("-m", "--module", dest="module",default='none',help="Nom du module")
parser.add_option("-d", "--db", dest="db",default='terp',help="Nom de la base ")
parser.add_option("-U", "--user", dest="user",default='terp',help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd",default='terp',help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host",default='127.0.0.1',help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port",default='8069',help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole",default='https',help="protocole http/https")
(options,args)= parser.parse_args()
if options.user == 'terp':
    options.user = options.db[:1].upper() + 'admin' + options.db[-1].upper()
    options.passwd = options.db[-1].upper() + 'ezorgan' + options.db[:1].upper()


try:
    connect_db=openerp_db(options.protocole+'://',options.host,options.port)
    connection=openerp(options.protocole+'://',options.host,options.port,options.db,options.user,options.passwd)  
except Exception, e:
    print "Erreur de connection ",e
    sys.exit(1)
    

db_module=module(connection)

#Mise à jour de la liste des modules
if options.action=='update_list':
    db_module.update_list()
elif options.action=="update_all":
    db_module.update_all()
elif options.action=="clean_all":
    db_module.clean_all()
elif options.action=='update':
    if options.module =="none":
        print "Vous devez donner un nom de module pour l'action update"
        sys.exit(1)
    else:
        db_module.update(options.module,force=options.force) 
elif options.action=='install':
    if options.module =="none":
        print "Vous devez donner un nom de module pour l'action install"
        sys.exit(1)
    else:
        print "install", options.module
        db_module.install(options.module) 
elif options.action=='remove':
    if options.module =="none":
        print "Vous devez donner un nom de module pour l'action uninstall"
        sys.exit(1)
    else:
        db_module.uninstall(options.module) 
elif options.action=='versioncourante':
    if options.module =="none":
        print "Vous devez donner un nom de module pour l'action versioncourante"
        sys.exit(1)
    else:
        db_module.versioncourante(options.module) 
else:
    print "Action invalide "
    sys.exit(1)
