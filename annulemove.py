#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import xmlrpclib
import sys
import time

base="currency_test"
serveur="192.168.12.17"
port="10013"
prot="https"
user="BadminI"
pwd="IezorganB"

server =xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/common')
uid= server.login(base,user, pwd)
sock = xmlrpclib.ServerProxy(prot+'://'+serveur+':'+port+'/xmlrpc/object')

 
 
pas=0
move_ids=sock.execute(base,uid,pwd,'account.move','search',[], 0 , 80000)
compteur=len(move_ids)
for move_id in move_ids:
    pas = pas + 1
    print pas,'/',compteur, move_id
    sock.execute(base,uid,pwd,'account.move','button_cancel',[move_id])
    
    move_line_ids=sock.execute(base,uid,pwd,'account.move.line','search',[('move_id','=',move_id)])
    recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_id',])
    recs = filter(lambda x: x['reconcile_id'], recs)
    rec_ids = [rec['reconcile_id'][0] for rec in recs]
    recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_partial_id',])
    recs = filter(lambda x: x['reconcile_partial_id'], recs)
    [rec_ids.append(rec['reconcile_partial_id'][0]) for rec in recs]
    if len(rec_ids):
        sock.execute(base,uid,pwd,'account.move.reconcile','unlink', rec_ids)
    sock.execute(base,uid,pwd,'account.move','unlink',[move_id])
    

print "ok"

