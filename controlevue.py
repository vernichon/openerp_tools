#!/usr/bin/python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import xmlrpclib
import sys
import time
import sqlite3
from odf.opendocument import Spreadsheet
from odf.opendocument import load
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.opendocument import OpenDocumentSpreadsheet

from odf.number import NumberStyle, DateStyle, CurrencyStyle, TextStyle, Number, Text, Day, Month, Year, Era
from odf.style import Style, TextProperties, TableColumnProperties, Map,TableCellProperties,TableRowProperties

from odf import text
from odf.text import P,Date
def addcell(tr,val,lestyle):

    if val == 'True':
        val = "Oui"
    if val == 'False':
        val = "Non"
    tc = TableCell(stylename = lestyle)
    tr.addElement(tc)
    p = P(text=val)
    tc.addElement(p)

def addcelldate(tr,val,stylename="dcs"):
    print dir(dcs)
    print dcs.qname
    tc = TableCell( valuetype ='date',datevalue=val,stylename=stylename)
    TableCell()
    tr.addElement(tc)

def cellpos(row,col):
    global rows
    cells = rows[row].getElementsByType(TableCell)
    retour = {}
    if col > (len(cells)-1):
        retour ['value'] = False
        return retour

    cell = cells[col]
    #print dir(cell)
    res = cell.getElementsByType(P)
   #
    retour = {}
    if len(res) >0:
        res = cell.getElementsByType(P)[0].firstChild
        #print dir(res)
        if 'data' in dir(res):
            retour['value'] = res.data
            if cell.attributes.has_key('table:formula'):
                retour['formule'] = cell.getAttribute('formula').replace('of:=','')
            return retour
        else:
            retour ['value'] = False

    else:
        retour ['value'] = False
    return retour

calc = OpenDocumentSpreadsheet()
WhiteStyle=Style(name='Blanc',family="table-cell")

WhiteStyle.addElement(TextProperties( fontweight="bold",fontfamily="Arial", fontsize="14pt"))

lestyle = WhiteStyle
dcs = DateStyle(name="dcs",formatsource="AAAA-MM-JJ")

widthshort = Style(name="Wshort", family="table-column")
widthshort.addElement(TableColumnProperties(columnwidth="5cm"))

widthlong = Style(name="Wshort", family="table-column")
widthlong.addElement(TableColumnProperties(columnwidth="15cm"))

calc.automaticstyles.addElement(dcs)
calc.automaticstyles.addElement(WhiteStyle)
calc.automaticstyles.addElement(widthshort)
calc.automaticstyles.addElement(widthlong)


row = 0



conn = sqlite3.connect("/usr/local/bin/serveurs.sqlite")
cr = conn.cursor()

cr.execute("select base,host,port,protocole from serveurs where base != 'ubis' order by base ")
for ligne in  cr.fetchall():
    base = ligne[0]
    host = ligne[1]
    port = str(ligne[2])
    prot = str(ligne[3])
    user = base[:1].upper()+'admin'+base[-1].upper()
    password = base[-1].upper()+'ezorgan'+base[:1].upper()
    host = "127.0.0.1"
    port = "8069"
    prot = "http://"

    table = Table(name=base)
    print
    print "----------------------  "+base+"  ------------------------------------------"
    print
    table.addElement(TableColumn(numbercolumnsrepeated=1,stylename=widthshort))
    table.addElement(TableColumn(numbercolumnsrepeated=2,stylename=widthlong))
    table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=widthshort))
    server =xmlrpclib.ServerProxy(prot+host+':'+port+'/xmlrpc/common',allow_none=True)
    uid= server.login(base,user, password)
    sock = xmlrpclib.ServerProxy(prot+host+':'+port+'/xmlrpc/object',allow_none=True)
    root=None
    account_ids=sock.execute(base,uid,password,'account.account','search',[('active','in',('True','False')),('type' ,'<>','view')],0,8000,'code')
    trouve = False
    for id in account_ids:
        search_child=sock.execute(base,uid,password,'account.account','search',[('active','in',('True','False')),('parent_id','=',id)],0,1000)
        if len(search_child) >0:
            if trouve == False:
                trouve = True
                tr = TableRow()
                table.addElement(tr)
                addcell(tr,"",lestyle)
                addcell(tr,base,lestyle)
            account=sock.execute(base,uid,password,'account.account','read',[id],['code','name','type','balance'])
            #if account[0]['balance'] <> 0 :
            tr = TableRow()
            table.addElement(tr)
            addcell(tr,"",lestyle)
            row = row + 1
            tr = TableRow()
            table.addElement(tr)

            addcell(tr,account[0]['code'],lestyle)
            addcell(tr,account[0]['name'],lestyle)
            addcell(tr,account[0]['type'],lestyle)
            addcell(tr,len(search_child),lestyle)
            addcell(tr,account[0]['balance'],lestyle)
#            print account[0]['code'],account[0]['name'].encode('utf-8')," "*(65-len(account[0]['name']))," type : ",account[0]['type'],' enfants : ', len(search_child),account[0]['balance']

            for child_id in search_child:
                account=sock.execute(base,uid,password,'account.account','read',[child_id],['code','name','type','balance'])
                search_child=sock.execute(base,uid,password,'account.account','search',[('active','in',('True','False')),('parent_id','=',child_id)],0,1000)
                row = row + 1
                tr = TableRow()
                table.addElement(tr)

                addcell(tr,"",lestyle)
                addcell(tr,account[0]['code'],lestyle)
                addcell(tr,account[0]['name'],lestyle)
                addcell(tr,account[0]['type'],lestyle)
                addcell(tr,len(search_child),lestyle)
                addcell(tr,account[0]['balance'],lestyle)
                #print "\t",account[0]['code'],account[0]['name'].encode('utf-8')," "*(65-len(account[0]['name']))," type : ",account[0]['type'],' enfants : ', len(search_child),account[0]['balance']

    if trouve:
        calc.spreadsheet.addElement(table)
calc.save('/home/evernichon/controle_vue',True)
