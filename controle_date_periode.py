#!/usr/bin/python
# -*- coding: utf-8 -*-
import openerp_connection

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



connection = openerp_connection.openerp(prot + '://', host, port, base, user, pwd)
move_ids = connection.search('account.move', [], 0, 8000000)


def date_periode(period_id):
    periode = connection.read('account.period', period_id, ['date_start', 'date_stop'])
    return [periode['date_start'], periode['date_stop']]


date_dif_periode = 0
date_dif_move_periode = 0
ligne_dif_move = 0
len_move = len(move_ids)
x = 0
for move_id in move_ids:
    x += 1
    print "%s / %s" % (x, len_move)

    move_line_ids = connection.search('account.move.line', [('move_id', '=', move_id)])
    move = connection.read('account.move', move_id, ['date', 'name', 'period_id'])
    date_periode_val = date_periode(move['period_id'][0])
    date_periode_start = date_periode_val[0]
    date_periode_stop = date_periode_val[1]
    if move['date'] < date_periode_start or move['date'] > date_periode_stop:
        print "move  ", move['id'], move['name'], move['date'], move['period_id'][1]
        date_dif_move_periode += 1
    for move_line_id in move_line_ids:
        move_line = connection.read('account.move.line', move_line_id,
                                    ['date', 'name', 'debit', 'credit', 'period_id', 'account_id'])
        date_periode_val = date_periode(move_line['period_id'][0])
        date_periode_start = date_periode_val[0]
        date_periode_stop = date_periode_val[1]
        if move_line['date'] < date_periode_start or move_line['date'] > date_periode_stop:
            print "move line ", move_line['date'], move_line['period_id'][1], move_line['account_id'][1], move_line['name'], \
            move_line['debit'], move_line['credit']
            date_dif_periode += 1

        if move_line['period_id'][0] != move['period_id'][0]:
            print "periode ecriture :=  periode ligne"
            print "move line ", move_line
            print
            ligne_dif_move += 1

print "ligne avec date hors periode ", date_dif_periode
print "move avec date hors periode ", date_dif_move_periode
print "ligne avec periode != periode move ", ligne_dif_move
