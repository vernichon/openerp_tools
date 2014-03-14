# -*- coding: utf-8 -*-
#!/usr/bin/python
from xml.dom.minidom import parse
import xmlrpclib
import sys
import base64
import time
from optparse import OptionParser

parser = OptionParser()

parser.add_option("-d", "--db", dest="db",help="database name")
parser.add_option("-U", "--user", dest="user",help="database user")
parser.add_option("-W", "--passwd", dest="passwd",help="database user password")
parser.add_option("-H", "--host", dest="host",help="postgres server")
parser.add_option("-P", "--prot", dest="prot",help="protocol http or https")
parser.add_option("-p", "--port", dest="port",help="postgres database port")

(options,args)= parser.parse_args()

base = options.db
user = options.user
pwd = options.passwd
serveur = options.host
port = options.port
prot = options.prot

try:
    server =xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/common')
    uid= server.login(base,user,pwd)
    sock = xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/report')
    obj = xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/object')
except:
    print "DBG unable to connect"
    sys.exit()


report_ids=obj.execute(base,uid,pwd,'ir.actions.report.xml','search',[],0,100)
name="account.invoice"  # nom du report , champ report_name dans la table ir_act_report_xml
model="account.invoice" # object utilisé pour le report, champ model dans la table ir_act_report_xml
  
maxattempt=20000
#ids=obj.execute(base,uid,pwd,'account.invoice','search',[('date_invoice','>','2010-08-31'),('type','=','out_invoice')])
ids=obj.execute(base,uid,pwd,'account.invoice','search',[('type','=','out_invoice')],0,8000)
for id in ids:
    datas ={'report_type': 'pdf',  'model': model, 'id': id} 
    ctx={'lang': 'fr_FR', 'tz': 'Europe/Paris'}
    
    invoice=obj.execute(base,uid,pwd,'account.invoice','read',id,['partner_id'])
    #print invoice['partner_id']
    report_id=sock.report(base,uid, pwd,  name,[id], datas, ctx)
    #print "Report Id : ",report_id,id
    state=False
    attempt=0
    
    while not state:
        try:
            val= sock.report_get(base,uid, pwd, report_id)
        except:
            print invoice['partner_id'][1].encode('iso-8859-15')
            #obj.exec_workflow(base,uid,pwd,'account.invoice','invoice_cancel',id)
            #obj.execute(base,uid,pwd,'account.invoice','action_cancel_draft',[id])
            val['state']=True
            val['result']=False
            pass
        state = val['state']
        if not state:
            time.sleep(1)
            attempt += 1  
            if attempt>maxattempt:
                print('Printing aborted, too long delay !')
                raise "erreur"
    if val['result']:
        content=base64.decodestring(val['result'])
        f=file(name+"-"+invoice['partner_id'][1].replace(' ','-')+'.pdf','wb')
        f.write(content)
        f.close()   

pass
    

