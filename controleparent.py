#!/usr/bin/python
# -*- coding: utf-8 -*-
import xmlrpclib

import psycopg2
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", default='terp', help="Nom de la base ")
parser.add_option("-U", "--user", dest="user", default='terp', help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd", default='terp', help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host", default='127.0.0.1', help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port", default='8069', help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole", default='https', help="protocole http/https")

(options, args) = parser.parse_args()
user = options.user
pwd = options.passwd
base = options.db
host = options.host
port = options.port
prot = options.protocole


connectstr = "host= %s user=%s password=%s dbname=%s" % ('127.0.0.1', 'postgres', 'postgres', base)
conn = psycopg2.connect(connectstr)
cr = conn.cursor()
trouve = False
server = xmlrpclib.ServerProxy(prot + '://' + host + ':' + port + '/xmlrpc/common', allow_none=True)
uid = server.login(base, user, password)
sock = xmlrpclib.ServerProxy(prot + '://' + host + ':' + port + '/xmlrpc/object', allow_none=True)

cr.execute('select parent_id from account_account where parent_id is not null group by parent_id order by parent_id')
trouve_db = False
for parent_id in cr.fetchall():
    trouve = False
    parent_id = parent_id[0]
    account_ids = sock.execute(base, uid, pwd, 'account.account', 'search', [('parent_id', '=', parent_id)], 0,
                               8000, 'code')
    for account_id in account_ids:
        account = sock.execute(base, uid, pwd, 'account.account', 'read', [account_id], None, None)
        if not account[0]['parent_id']:
            pass
        else:
            parent = sock.execute(base, uid, pwd, 'account.account', 'read', account[0]['parent_id'][0],
                                  ['active', 'code', 'name'])
            #print parent
            if not parent['active']:
                if not trouve_db:
                    print
                    print
                    "----------------------  " + base + "  ------------------------------------------"
                    print
                    trouve_db = True
                if not trouve:
                    print
                    "Parent inactif ", parent['code'], parent['name'].encode('utf-8').strip()
                    print
                trouve = True
                print
                "\t\tCompte : ", account[0]['code'], ' ', account[0]['name'].encode('utf-8').strip(), " " * (
                    100 - len(account[0]['name'].encode('utf-8').strip()))

                print
