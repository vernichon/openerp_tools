#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmlrpclib
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", default='terp', help="Nom de la base ")
parser.add_option("-U", "--user", dest="user", default='terp', help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd", default='terp', help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host", default='127.0.0.1', help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port", default='8069', help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole", default='https', help="protocole http/https")
(options, args) = parser.parse_args()

base = options.db
serveur = options.host
port = options.port
prot = options.protocole
user = options.user
pwd = options.passwd

server = xmlrpclib.ServerProxy(prot + '://' + serveur + ':' + port + '/xmlrpc/common')
uid = server.login(base, user, pwd)
sock = xmlrpclib.ServerProxy(prot + '://' + serveur + ':' + port + '/xmlrpc/object')

invoice_ids = sock.execute(base, uid, pwd, 'account.invoice', 'search', [('state', '!=', 'draft')], 0 , 80000)
pas = 0
compteur = len(invoice_ids)
for invoice_id in invoice_ids:
    pas += 1
    move_id = sock.execute(base, uid, pwd, 'account.invoice', 'read', [invoice_id])
    print pas, '/', compteur, move_id[0]['number']
    if move_id[0]['move_id']:
        move_id = move_id[0]['move_id'][0]
        move_line_ids = sock.execute(base, uid, pwd, 'account.move.line', 'search', [('move_id', '=', move_id)])
        recs = sock.execute(base, uid, pwd, 'account.move.line', 'read', move_line_ids, ['reconcile_id', ])
        recs = filter(lambda x: x['reconcile_id'], recs)
        rec_ids = [rec['reconcile_id'][0] for rec in recs]
        recs = sock.execute(base, uid, pwd, 'account.move.line', 'read', move_line_ids, ['reconcile_partial_id', ])
        recs = filter(lambda x: x['reconcile_partial_id'], recs)
        [rec_ids.append(rec['reconcile_partial_id'][0]) for rec in recs]
        if len(rec_ids):
            sock.execute(base, uid, pwd, 'account.move.reconcile', 'unlink', rec_ids)
    sock.execute(base, uid, pwd, 'account.invoice', 'action_cancel_draft', [invoice_id])
    sock.exec_workflow(base, uid, pwd, 'account.invoice', 'invoice_cancel', invoice_id)
    sock.execute(base, uid, pwd, 'account.invoice', 'action_cancel_draft', [invoice_id])

print "ok"

