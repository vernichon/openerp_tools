#!usr/bin/python2.4
# -*- coding: utf-8 -*-
"""
    Script utilisé pour annuler les relevés de banques
"""
import xmlrpclib
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", default='terp', help="Nom de la base ")
parser.add_option("-U", "--user", dest="user", default='terp', help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd", default='terp', help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host", default='127.0.0.1', help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port", default='8069', help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole", default='http', help="protocole http/https")
parser.add_option("-i", "--id", dest="bnk_st_id", default=0, help="Invoice ID")
parser.add_option("-s", "--pattern", dest="pattern", default="[('state', '!=', 'draft')]", help="Pattern search for Bank Statement")

(options, args) = parser.parse_args()
user = options.user
pwd = options.passwd
base = options.db
host = options.host
port = options.port
proto = options.protocole

url = proto + '://' + host + ':' + port
server = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
uid = server.login(base, user, pwd)
sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')
if options.bnk_st_id == 0:
    st_ids = sock.execute(base, uid, pwd, 'account.bank.statement', 'search', eval(options.pattern), 0 , 80000)
else:
    st_ids = [int(options.bnk_st_id)]


for st_id in st_ids:
    print "processing bank_statement %s" % st_id
    st = sock.execute(base, uid, pwd, 'account.bank.statement', 'read', [st_id])
    line_st_ids = sock.execute(base, uid, pwd, 'account.bank.statement.line', 'search', [('statement_id', '=', st_id)])
    lines = sock.execute(base, uid, pwd, 'account.bank.statement.line', 'read', line_st_ids)
    for line in lines:
        move_line_ids = sock.execute(base, uid, pwd, 'account.move.line', 'search',
                                     [('move_id', 'in', line['move_ids'])])

        recs = sock.execute(base, uid, pwd, 'account.move.line', 'read', move_line_ids, ['reconcile_id'])
        recs = filter(lambda x: x['reconcile_id'], recs)
        rec_ids = [rec['reconcile_id'][0] for rec in recs]

        recs = sock.execute(base, uid, pwd, 'account.move.line', 'read', move_line_ids, ['reconcile_partial_id'])
        recs = filter(lambda x: x['reconcile_partial_id'], recs)
        [rec_ids.append(rec['reconcile_partial_id'][0]) for rec in recs]

        if len(rec_ids):
            sock.execute(base, uid, pwd, 'account.move.reconcile', 'unlink', rec_ids)
        #recs=sock.execute(base,uid,pwd,'account.move.line','read',move_line_ids,['reconcile_partial_id',])
        sock.execute(base, uid, pwd, 'account.move', 'button_cancel', line['move_ids'])
        sock.execute(base, uid, pwd, 'account.move', 'unlink', line['move_ids'])

    sock.execute(base, uid, pwd, 'account.bank.statement', 'button_cancel', [st_id])

