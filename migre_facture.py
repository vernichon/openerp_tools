#!/usr/bin/python
# -*- encoding: utf-8 -*-

import openerp_connection
from optparse import OptionParser

PARSER = OptionParser()
PARSER.add_option("-a", "--userdb", dest="userdb", default='postgres', help="User Postgres db")
PARSER.add_option("-b", "--passwordb", dest="passdb", default='admin', help="Password User Postgres db")
PARSER.add_option("-d", "--dbs", dest="dbs", default='terp', help="Nom de la base source")
PARSER.add_option("-u", "--users", dest="users", default='terp', help="User Openerp source")
PARSER.add_option("-w", "--passwds", dest="passwds", default='terp', help="mot de passe Openerp  source")
PARSER.add_option("-s", "--serveurs", dest="hosts", default='127.0.0.1', help="Adresse  Serveur source")
PARSER.add_option("-o", "--ports", dest="ports", default='8069', help="port du serveur source")
PARSER.add_option("-p", "--protocoles", dest="protocoles", default='http', help="protocole http/https source")
PARSER.add_option("-D", "--dbc", dest="dbc", default='testmulti', help="Nom de la base cible ")
PARSER.add_option("-U", "--userc", dest="userc", default='terp', help="User Openerp cible")
PARSER.add_option("-W", "--passwdc", dest="passwdc", default='terp', help="mot de passe Openerp cible  ")
PARSER.add_option("-S", "--serveurc", dest="hostc", default='127.0.0.1', help="Adresse  Serveur cible")
PARSER.add_option("-O", "--portc", dest="portc", default='8090', help="port du serveur cible")
PARSER.add_option("-P", "--protocolec", dest="protocolec", default='http', help="protocole http/https cible")
(OPTIONS, ARGUMENTS) = PARSER.parse_args()




BASECIBLE = OPTIONS.dbc
BASESOURCE = OPTIONS.dbs

CONNECTION_CIBLE = openerp_connection.openerp(OPTIONS.protocolec + '://',
                                              OPTIONS.hostc, OPTIONS.portc, BASECIBLE, OPTIONS.userc, OPTIONS.passwdc)

CONNECTION_SOURCE = openerp_connection.openerp(OPTIONS.protocoles + '://',
                                               OPTIONS.hosts, OPTIONS.ports, BASESOURCE, OPTIONS.users, OPTIONS.passwds)

print "CONNECTION_SOURCE ", CONNECTION_SOURCE
print "CONNECTION_CIBLE  ", CONNECTION_CIBLE

invoice_ids = CONNECTION_SOURCE.search('account.invoice', [('date_invoice', '>=', '2013-03-18')], 0, 100000)
invoice_fields_type = CONNECTION_CIBLE.exec_act('account.invoice', 'fields_get')
invoice_line_fields_type = CONNECTION_CIBLE.exec_act('account.invoice.line', 'fields_get')

for invoice_id in invoice_ids:

    invoice = CONNECTION_SOURCE.read('account.invoice', invoice_id)
    invoice.pop('invoice_line')
    invoice.pop('tax_line')
    invoice.pop('move_id')
    invoice.pop('id')
    facture = invoice.copy()
    for x in invoice:
        if invoice[x] and invoice_fields_type[x]['type'] == 'many2one':
            facture[x] = invoice[x][0]

    facture['state'] = 'draft'
    new_invoice_id = CONNECTION_CIBLE.create('account.invoice', facture)
    print "invoice id ", invoice_id
    if invoice_id:
        invoice_line_ids = CONNECTION_SOURCE.search('account.invoice.line', [('invoice_id', '=', invoice_id)])
        for invoice_line_id in invoice_line_ids:
            invoice_line = CONNECTION_SOURCE.read('account.invoice.line', invoice_line_id)
            invoice_line.pop('id')
            for f in invoice_line:
                if invoice_line[f] and invoice_line_fields_type[f]['type'] == 'many2one':
                    invoice_line[f] = invoice_line[f][0]
            invoice_line['invoice_id'] = new_invoice_id
            CONNECTION_CIBLE.create('account.invoice.line', invoice_line)

    print invoice

print "invoice_ids  ", invoice_ids
print len(invoice_ids)
