#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
import xmlrpclib


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

(options,args)= parser.parse_args()


connectstr="host= %s user=%s password=%s dbname=%s"%(options.host,options.userdb,options.passwddb,options.db)
conn = psycopg2.connect(connectstr)
cr = conn.cursor()
connect=[(options.db,options.user,options.passwd)]
for (base,user,pwd) in connect:
    server=xmlrpclib.ServerProxy(options.protocole+'://'+options.host+':'+options.port+'/xmlrpc/common')
    uid= server.login(base,user, pwd)
    sock = xmlrpclib.ServerProxy(options.protocole+'://'+options.host+':'+options.port+'/xmlrpc/object')
    model_ids = sock.execute(base,uid,pwd,'ir.model','search',[('model','!=','res_users')])
    models=sock.execute(base,uid,pwd,'ir.model','read',model_ids,['model'])
    models.sort(lambda x,y : cmp(x['model'], y['model']))
    cr.execute("select tablename from pg_tables where schemaname='public'")
    tables=[x[0] for x in cr.fetchall()]                  
    for model in models:
       # print model['model']
        
       # print req
        if model['model'].replace('.','_') in tables:
            fields=None
            try:
                fields=sock.execute(base,uid,pwd,model['model'],'fields_get')
            except:
                pass
            
            if fields:
                req="SELECT column_name FROM information_schema.columns WHERE table_name ='%s'" % model['model'].replace('.','_')
                cr.execute(req)
                for ligne in cr.fetchall():
                    if (ligne[0] not in fields) and ligne[0]    not in ('id','perm_id','create_uid','create_date','write_date','write_uid'):
                        print "Champ %s de la table %s inexistant dans la definition de l'objet "% (ligne[0],model['model'])
                        req='alter table %s drop column %s cascade' % (model['model'].replace('.','_'),ligne[0])
                        print req
                        res=cr.execute(req)
                        print res
                        conn.commit()
print "That's all folks!"
