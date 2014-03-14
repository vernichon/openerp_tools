#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import psycopg2
try:
    base = sys.argv[1]
    user = sys.argv[2]
    host = sys.argv[3]
except:
    print "Vous devez fournir un nom de base"
    sys.exit()

#userdb="user_"+user
#pwddb="pass_postgres.openerp"+user
userdb="evernichon"
pwddb="saikaku"
db = psycopg2.connect("host= "+host+" port='5432' user="+userdb+"  password="+pwddb+" dbname="+base)
cr = db.cursor()

cr.execute("SELECT relname  FROM pg_class WHERE relkind = 'S'")
sequences=cr.fetchall()
for x in sequences:
    try:
        cr.execute("select last_value from "+x[0])
        seq=x[0]
        table=seq.replace('_id_seq','')
        last=cr.fetchone()[0]
        print table
        cr.execute("select max(id) from "+table)
        max=cr.fetchone()[0]
        if max:
            if last>1 and last-max<0:
                print seq," ",last," ",table," ",max
                cr.execute("SELECT setval('"+seq+"',"+str(max+1)+");")
                print "SELECT setval('"+seq+"',"+str(max+1)+");"
    except:
        pass
cr.close()
print "Recree Sequence"
