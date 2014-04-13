#!/usr/bin/env python

import os
import sys

file = sys.argv[1]

fp = open(file, 'r')

for l in fp.readlines():
    data = l.split()
    if 1:
        cmd = "mysql --user=%s --password=%s -h sdb.salt \
        -D sdb -e \"INSERT INTO MassDimm \
        VALUES(\'%s %s\', NULL, %s%s) on duplicate key update Dimm=%s;\"" % \
        (os.environ['MASSSQL'], os.environ['MASSPASS'],
         data[0], data[1], data[4], ", NULL" * 26, data[4]) 
        #print cmd
        os.system(cmd)
    try:
        pass
    except Exception, e:
        print "DB ERROR: %s" % e
        break
