#!/usr/bin/python
# -*- coding: utf-8 -*-
import xmlrpclib

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", default='terp', help="Nom de la base ")
parser.add_option("-U", "--user", dest="user", default='admin', help="User Openerp")
parser.add_option("-W", "--passwd", dest="passwd", default='admin', help="mot de passe Openerp ")
parser.add_option("-H", "--host", dest="host", default='192.168.12.252', help="Adresse  Serveur")
parser.add_option("-p", "--port", dest="port", default='8069', help="port du serveur")
parser.add_option("-P", "--protocole", dest="protocole", default='http', help="protocole http/https")

(options, args) = parser.parse_args()


server = xmlrpclib.ServerProxy(options.protocole + '://' + options.host + ':' + options.port + '/xmlrpc/common')
uid = server.login(options.db, options.user, options.passwd)
sock = xmlrpclib.ServerProxy(options.protocole + '://' + options.host + ':' + options.port + '/xmlrpc/object')
values_ids = sock.execute(options.db, uid, options.passwd, 'ir.values', 'search', [], 0, 80000, 'value')
for value in sock.execute(options.db, uid, options.passwd, 'ir.values', 'read', values_ids):
    if "ir.actions" in value['value']:
        (model, value_id) = value['value'].split(',')
        res = None
        res = sock.execute(options.db, uid, options.passwd, model, 'search', [('id', '=', int(value_id))])
        if not res:
            print "Supression %s , id : %s" % (model, value_id)
            res = sock.execute(options.db, uid, options.passwd, "ir.values", 'unlink', value['id'])

print "Fin Clean Ir Values"
