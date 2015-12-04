#!/usr/bin/python

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



def scope_status(g):
    ''' Get the current status of the telescope'''
    
    scope = {}
    scope['ra'] = g.ra()
    scope['dec'] = g.dec()
    scope['lst'] = g.lst()
    scope['ha'] = Angle('%s hour' % lst) - Angle('%s hour' % ra)
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
    g = GTO900()
    o = OxWagon()
    
    # make sure the telescope remains switched on
    o.scope()    
    
    scope = scope_status(g)
    
    

    
    
    
    
