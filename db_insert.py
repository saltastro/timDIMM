#!/usr/bin/env python

import os
import sys

file = sys.argv[1]

fp = open(file, 'r')

for l in fp.readlines():
    data = l.split()
    try:
        cmd = "mysql5 --user=%s --password=%s -h sdb.salt \
        -D sdb -e \"INSERT INTO MassDimm \
        VALUES(\'%s %s\', NULL, %s, NULL, NULL, NULL, NULL, NULL, NULL);\"" % \
        (os.environ['MASSSQL'], os.environ['MASSPASS'],
         data[0], data[1], data[4])
        #print cmd
        os.system(cmd)
    except Exception, e:
        print "DB ERROR: %s" % e
        break
