#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import xmlrpclib
import sys
import time

base="mmq"
serveur="mmq.uniforme.ch"
port="9069"
prot="https"
user="MadminQ"
pwd="QezorganM"

server =xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/common')
uid= server.login(base,user, pwd)
sock = xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/object')

#invoice_ids = sock.execute(base, uid, pwd, 'account.invoice', 'search', [('state','!=', 'draft')],0 , 80000)
pas=0
invoice_ids=[4087]
compteur=len(invoice_ids)
for id in invoice_ids:
    pas=pas+1
    move_id=sock.execute(base,uid,pwd,'account.invoice','read',[id])
    print pas,'/',compteur,move_id[0]['number']
    if move_id[0]['move_id']:
        move_id=move_id[0]['move_id'][0]
        move_line_ids=sock.execute(base,uid,pwd,'account.move.line','search',[('move_id','=',move_id)])
        recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_id',])
        recs = filter(lambda x: x['reconcile_id'], recs)
        rec_ids = [rec['reconcile_id'][0] for rec in recs]
        recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_partial_id',])
        recs = filter(lambda x: x['reconcile_partial_id'], recs)
        [rec_ids.append(rec['reconcile_partial_id'][0]) for rec in recs]
        if len(rec_ids):
            sock.execute(base,uid,pwd,'account.move.reconcile','unlink', rec_ids)
        #recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_partial_id',])
    #    sock.execute(base,uid,pwd,'account.move','button_cancel',[move_id])
    #    sock.execute(base,uid,pwd,'account.move','unlink',[move_id])
    #mv_ids=sock.execute(base,uid,pwd,'account.move','search',[('invoice_id','=',id)])
    #if mv_ids:
    #    print mv_ids
    #    for mv_id in mv_ids:
    #        print "button cancel",sock.execute(base,uid,pwd,'account.move','button_cancel',[mv_id])
    #        print "unlink",sock.execute(base,uid,pwd,'account.move','unlink',[mv_id])

    sock.execute(base,uid,pwd,'account.invoice','action_cancel_draft',[id])
    #print sock.exec_workflow(base,uid,pwd,'account.invoice','invoice_cancel',id)
    sock.exec_workflow(base,uid,pwd,'account.invoice','invoice_cancel',id)
    sock.execute(base,uid,pwd,'account.invoice','action_cancel_draft',[id])
    #sock.exec_workflow(base,uid,pwd,'account.invoice','invoice_open',id)

print "ok"

