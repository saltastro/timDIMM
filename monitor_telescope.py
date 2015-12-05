#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 01:03:08 2015

@author: jpk

This monitors the telescope position during the day when the telescope is not
in use. 

It will park the telescope facing South using:
Alt=+32:06:03, Az = +174:22:03

The scripts also monitors the local time of the mount and syncs the if it is 
out of sync
"""
from pygto900 import GTO900
from ox_wagon import OxWagon
import datetime as datetime
from astropy.coordinates import Angle
import os


def scope_status(g):
    ''' Get the current status of the telescope'''
    
    scope = {}
    scope['ra'] = g.ra()
    scope['dec'] = g.dec()
    scope['lst'] = g.lst()
    scope['ha'] = Angle('%s hour' % scope['lst']) - Angle('%s hour' % scope['ra'])
    scope['alt'] = g.alt()
    scope['az'] = g.az()
    scope['p'] = g.pier()
    scope['time'] = g.get_local_time()
    
    return scope

def send_to_park_position(g):
    ''' Command the telescope to the alt az coords listed above '''
    g.startup()  
    g.command_alt(32,06,03)
    g.command_az(174,22,03)
    g.slew()
        
def check_position(g, scope):
    '''Check where the telescope is compared to the alt az values'''
    pass
    
    
    
if __name__ == '__main__':

    if not os.path.isfile('timDIMM_rinning'):
        g = GTO900()
        o = OxWagon()
        o_status = o.status()
        if o_status['Drop Roof Closed'] and o_status['Slide Roof Closed']:
            print
            print datetime.datetime.now() 
            # make sure the telescope remains switched on
            print 'keeping the scope on by sending the close command'
            o.close()    
            print 'parking the mount'
            g.park_mode()
            #scope = scope_status(g)
            print
        else:
            print datetime.datetime.now()
            print 'The ox wagon is opening, or not closed, Don\'t do anything'
            pass
    else:
        print datetime.datetime.now()
        print 'timdimm software is running, doing nothing'
        pass

    
    
    
    
