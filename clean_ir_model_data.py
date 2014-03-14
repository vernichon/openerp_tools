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
parser.add_option("-t", "--table", dest="table", default=False, help="modele")

(options, args) = parser.parse_args()

connect = [(options.db, options.user, options.passwd)]
for (base, user, pwd) in connect:
    server = xmlrpclib.ServerProxy(options.protocole + '://' + options.host + ':' + options.port + '/xmlrpc/common')
    uid = server.login(base, user, pwd)
    sock = xmlrpclib.ServerProxy(options.protocole + '://' + options.host + ':' + options.port + '/xmlrpc/object')
    if not options.table:
        model_ids = sock.execute(base, uid, pwd, 'ir.model', 'search', [('model', '!=', 'res_users')])
    else:
        model_ids = sock.execute(base, uid, pwd, 'ir.model', 'search', [('model', '=', options.table)])
    models = sock.execute(base, uid, pwd, 'ir.model', 'read', model_ids, ['model'])
    models.sort(lambda x, y: cmp(x['model'], y['model']))
    for model in models:
        print model['model']
        model_data_ids = sock.execute(base, uid, pwd, 'ir.model.data', 'search', [('model', "=", model['model'])])
        for model_data_id in model_data_ids:
            model_data = sock.execute(base, uid, pwd, 'ir.model.data', 'read', model_data_id, ['model', 'res_id'])
            #~ print model['model']
            try:
                if "active" in sock.execute(base, uid, pwd, model_data['model'], 'fields_get'):
                    recherche = [('id', '=', model_data['res_id']), ('active', 'in', ('True', 'False'))]
                else:
                    recherche = [('id', '=', model_data['res_id'])]
            except:
                pass
            res = False
            try:
                res = sock.execute(base, uid, pwd, model_data['model'], 'search', recherche)
            except:
                pass
            if not res:
                print "Suppression", base, model_data_id, model_data['model'], model_data['res_id']
                sock.execute(base, uid, pwd, 'ir.model.data', 'unlink', model_data['id'])
                ir_values_ids = sock.execute(base, uid, pwd, 'ir.values', 'search',
                                             [('value', "=", "%s,%s" % (model_data['model'], model_data['res_id']))])
                sock.execute(base, uid, pwd, 'ir.values', 'unlink', ir_values_ids)

print "That's all folks!"
