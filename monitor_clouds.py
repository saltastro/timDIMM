#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 20:30:53 2015

@author: jpk

A script that will keep the ox wagon sliding roof open until q is pressed

"""

import time
from ox_wagon import OxWagon

o = OxWagon()

try:
    while True:
        print
        print '*****************************************************'
        print 'Opening the ox wagon to monitor clouds, waiting 5min'
        print
        print 'Press Ctrl-c to exit the monitoring script, it will '
        print 'close the ox wagon'
        print '*****************************************************'
        print
        o.monitor()
        time.sleep(300)
        
except KeyboardInterrupt:
    print 'Closing the ox_wagon now'
    o.close_scope_on()
    exit