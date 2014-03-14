#!/usr/bin/python
# -*- coding: utf-8 -*-
import xmlrpclib
import sqlite3
import psycopg2




conn = sqlite3.connect("/usr/local/bin/serveurs.sqlite")
cr = conn.cursor()
print "                  Compte parent sans type vue "
#cr.execute("select base,host,port from serveurs where base = 'vigi'")
cr.execute("select base,host,port from serveurs where base > 's4l' and base <> 'ubis' order by base")
for ligne in  cr.fetchall():
    

    base = ligne[0]
    host = ligne[1]
    port = str(ligne[2])
    user = base[:1].upper()+'admin'+base[-1].upper()
    password = base[-1].upper()+'ezorgan'+base[:1].upper()
    pwd = password
    host = "127.0.0.1"
    connectstr="host= %s user=%s password=%s dbname=%s"%('127.0.0.1','eric','saikaku',base)
    conn = psycopg2.connect(connectstr) 
    cr = conn.cursor()
    prot='http'
    port = "8069"
    trouve = False
    server =xmlrpclib.ServerProxy(prot+'://'+host+':'+port+'/xmlrpc/common',allow_none=True)
    uid= server.login(base,user, password)
    sock = xmlrpclib.ServerProxy(prot+'://'+host+':'+port+'/xmlrpc/object',allow_none=True)
    
    cr.execute('select parent_id from account_account where parent_id is not null group by parent_id order by parent_id')
    trouve_db = False
    for account_id in  cr.fetchall():
        trouve = False
        account_id = account_id[0]
        account_ids=sock.execute(base,uid,pwd,'account.account','search',[('parent_id' ,'=',account_id)],0,8000,'code')
        for id in  account_ids:
            account=sock.execute(base,uid,pwd,'account.account','read',[id],None,None)
            if not account[0]['parent_id']:
                pass #print "Pas de parent ",account[0]['code'],account[0]['name'].encode('utf-8')
            else:
                parent = sock.execute(base,uid,pwd,'account.account','read',account[0]['parent_id'][0],['active','code','name'])
                #print parent
                if not parent['active']:
                    if not trouve_db:
                        print              
                        print "----------------------  "+base+"  ------------------------------------------"
                        print 
                        trouve_db = True
                    if not trouve :
                       
                        print "Parent inactif ", parent['code'],parent['name'].encode('utf-8').strip()
                        print 
                    trouve = True 
                    print "\t\tCompte : ",account[0]['code'],' ',account[0]['name'].encode('utf-8').strip()," "*(100-len(account[0]['name'].encode('utf-8').strip()))
                    
                    print 
                    #sock.execute(base,uid,pwd,'account.account','write',account[0]['parent_id'][0],{'active':True})
    conn.close()
