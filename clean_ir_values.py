#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import xmlrpclib


from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d", "--db", dest="db",default='fiefmgt',help="Nom de la base ")
parser.add_option("-U", "--user", dest="user",default='FadminT',help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd",default='TezorganF',help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host",default='192.168.12.252',help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port",default='8069',help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole",default='http',help="protocole http/https")

(options,args)= parser.parse_args()
if options.user == 'terp':
    options.user = options.db[:1].upper()+'admin'+options.db[-1].upper()
    options.passwd = options.db[-1].upper()+'ezorgan'+options.db[:1].upper()
connect=[(options.db,options.user,options.passwd)]
for (base,user,pwd) in connect:
    server=xmlrpclib.ServerProxy(options.protocole+'://'+options.host+':'+options.port+'/xmlrpc/common')
    uid= server.login(base,user, pwd)
    sock = xmlrpclib.ServerProxy(options.protocole+'://'+options.host+':'+options.port+'/xmlrpc/object')
    values_ids = sock.execute(base,uid,pwd,'ir.values','search',[],0,80000,'value')
    for value in sock.execute(base,uid,pwd,'ir.values','read',values_ids):
        if "ir.actions" in value['value']:
            (model,id) = value['value'].split(',')
            res=None
            res=sock.execute(base,uid,pwd,model,'search',[('id','=',int(id))])
            if not res:
                print "Supression %s , id : %s"%(model,id)
                res=sock.execute(base,uid,pwd,"ir.values",'unlink',value['id'])
#        model_data_ids = sock.execute(base,uid,pwd,'ir.model.data','search',[('model',"=",model['model'])])
#        for id in model_data_ids:
#	    model_data=sock.execute(base,uid,pwd,'ir.model.data','read',id,['model','res_id'])
#            #~ print model['model']
#            if "active" in sock.execute(base,uid,pwd,model_data['model'],'fields_get'):
#                recherche=[('id','=',model_data['res_id']),('active','in',('True','False'))]
#            else:
#                recherche=[('id','=',model_data['res_id'])]
#            if not sock.execute(base,uid,pwd,model_data['model'],'search',recherche):
#                print "Suppression",base,id,model_data['model'],model_data['res_id']
#                sock.execute(base,uid,pwd,'ir.model.data','unlink',model_data['id'])
#                ir_values_ids=sock.execute(base,uid,pwd,'ir.values','search',[('value',"=","%s,%s"%(model_data['model'],model_data['res_id']))])
#                sock.execute(base,uid,pwd,'ir.values','unlink',ir_values_ids)
#
print "Fin Clean Ir Values"
