#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 20:30:53 2015

@author: jpk

A script that will keep the ox wagon sliding roof open until Ctrl-c is pressed

"""
import datetime as d
import time
from ox_wagon import OxWagon
import os
o = OxWagon()
os.system('touch timDIMM_running')

try:
    while True:
        print
        print d.datetime.now()
        print '*****************************************************'
        print 'Opening the ox wagon to monitor clouds, waiting 5min'
        print
        print 'Press Ctrl-c to exit the monitoring script'
        print '*****************************************************'
        print
        o.monitor()
        time.sleep(300)
        
except KeyboardInterrupt:
    while True: 
        option = raw_input(' Would you like to open (o) or close (c) the ox wagon. Or exit (e) the script? <Option> then press <Enter>\n')
        if option == 'o':
            print 'Opening the ox wagon fully\n'
            o.open()
            os.system('rm timDIMM_running')
            break
        if option == 'c':
            print 'Closing the ox wagon\n'
            o.close_scope_off()
            os.system('rm timDIMM_running')
            break
        if option =='e':
            print 'The ox wagon will close shortly\n'
            os.system('rm timDIMM_running')
            break
