#!/usr/bin/python
# -*- coding: utf-8 -*-

import xmlrpclib
from optparse import OptionParser
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.opendocument import OpenDocumentSpreadsheet

def addcell(tr, val, lestyle):
    if val == 'True':
        val = "Oui"
    if val == 'False':
        val = "Non"
    tc = TableCell(stylename=lestyle)
    tr.addElement(tc)
    p = P(text=val)
    tc.addElement(p)


def addcelldate(tr, val, stylename="dcs"):
    tc = TableCell(valuetype='date', datevalue=val, stylename=stylename)
    TableCell()
    tr.addElement(tc)


def cellpos(row, col):
    global rows
    cells = rows[row].getElementsByType(TableCell)
    retour = {}
    if col > (len(cells) - 1):
        retour['value'] = False
        return retour

    cell = cells[col]
    res = cell.getElementsByType(P)
    retour = {}
    if len(res) > 0:
        res = cell.getElementsByType(P)[0].firstChild
        #print dir(res)
        if 'data' in dir(res):
            retour['value'] = res.data
            if 'table:formula' in cell.attributes:
                retour['formule'] = cell.getAttribute('formula').replace('of:=', '')
            return retour
        else:
            retour['value'] = False

    else:
        retour['value'] = False
    return retour


calc = OpenDocumentSpreadsheet()
WhiteStyle = Style(name='Blanc', family="table-cell")

WhiteStyle.addElement(TextProperties(fontweight="bold", fontfamily="Arial", fontsize="14pt"))

lestyle = WhiteStyle
dcs = DateStyle(name="dcs", formatsource="AAAA-MM-JJ")

widthshort = Style(name="Wshort", family="table-column")
widthshort.addElement(TableColumnProperties(columnwidth="5cm"))

widthlong = Style(name="Wshort", family="table-column")
widthlong.addElement(TableColumnProperties(columnwidth="15cm"))

calc.automaticstyles.addElement(dcs)
calc.automaticstyles.addElement(WhiteStyle)
calc.automaticstyles.addElement(widthshort)
calc.automaticstyles.addElement(widthlong)

row = 0





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
table = Table(name=base)
print
print
"----------------------  " + base + "  ------------------------------------------"
print
table.addElement(TableColumn(numbercolumnsrepeated=1, stylename=widthshort))
table.addElement(TableColumn(numbercolumnsrepeated=2, stylename=widthlong))
table.addElement(TableColumn(numbercolumnsrepeated=3, stylename=widthshort))
server = xmlrpclib.ServerProxy(prot + host + ':' + port + '/xmlrpc/common', allow_none=True)
uid = server.login(base, user, password)
sock = xmlrpclib.ServerProxy(prot + host + ':' + port + '/xmlrpc/object', allow_none=True)
root = None
account_ids = sock.execute(base, uid, password, 'account.account', 'search',
                           [('active', 'in', ('True', 'False')), ('type', '<>', 'view')], 0, 8000, 'code')
trouve = False
for account_id in account_ids:
    search_child = sock.execute(base, uid, password, 'account.account', 'search',
                                [('active', 'in', ('True', 'False')), ('parent_id', '=', account_id)], 0, 1000)
    if len(search_child) > 0:
        if not trouve:
            trouve = True
            tr = TableRow()
            table.addElement(tr)
            addcell(tr, "", lestyle)
            addcell(tr, base, lestyle)
        account = sock.execute(base, uid, password, 'account.account', 'read', [account_id],
                               ['code', 'name', 'type', 'balance'])
        #if account[0]['balance'] <> 0 :
        tr = TableRow()
        table.addElement(tr)
        addcell(tr, "", lestyle)
        row += 1
        tr = TableRow()
        table.addElement(tr)

        addcell(tr, account[0]['code'], lestyle)
        addcell(tr, account[0]['name'], lestyle)
        addcell(tr, account[0]['type'], lestyle)
        addcell(tr, len(search_child), lestyle)
        addcell(tr, account[0]['balance'], lestyle)
        #            print account[0]['code'],account[0]['name'].encode('utf-8')," "*(65-len(account[0]['name']))," type : ",account[0]['type'],' enfants : ', len(search_child),account[0]['balance']

        for child_id in search_child:
            account = sock.execute(base, uid, password, 'account.account', 'read', [child_id],
                                   ['code', 'name', 'type', 'balance'])
            search_child = sock.execute(base, uid, password, 'account.account', 'search',
                                        [('active', 'in', ('True', 'False')), ('parent_id', '=', child_id)], 0,
                                        1000)
            row += 1
            tr = TableRow()
            table.addElement(tr)

            addcell(tr, "", lestyle)
            addcell(tr, account[0]['code'], lestyle)
            addcell(tr, account[0]['name'], lestyle)
            addcell(tr, account[0]['type'], lestyle)
            addcell(tr, len(search_child), lestyle)
            addcell(tr, account[0]['balance'], lestyle)
            #print "\t",account[0]['code'],account[0]['name'].encode('utf-8')," "*(65-len(account[0]['name']))," type : ",account[0]['type'],' enfants : ', len(search_child),account[0]['balance']

if trouve:
    calc.spreadsheet.addElement(table)
calc.save('/home/evernichon/controle_vue', True)
