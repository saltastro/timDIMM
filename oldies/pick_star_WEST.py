#!/usr/bin/env python
import os
import hrstar_with_precess_WEST
import hrstar_with_precess
import hrstar
from pygto900 import GTO900, status, slew, airmass
import time

from astropy.coordinates import Angle

def pick_star(g, scope=None):
    """A task to check to see if the current star is okay, and if not,
       to find a new star and move to it.
    """

    current_file = 'current_object'
    exposure_file = 'exptime'
    salt_lat=Angle("-32:22:32 degree")
    catalog = 'star.lst'
    
    if scope == None:
        #ra,dec,ha,lst,alt,az,airmass,pier = status(g)
        alt = Angle('%s degree' % g.alt())
        az = Angle('%s degree' % g.az())
        pier = g.pier().strip().lower()
        lst = g.lst()
    else:
        alt = scope['alt']
        az = scope['az']
        pier = scope['pier']
        lst = scope['lst'].to_string().replace('h',':').replace('m',':').strip('s')
        
    #ha = Angle('%s hour' % g.lst()) - Angle('%s hour' % g.ra())
    ### TO AVOID RUNNING INTO THE PIER WHILE TRACKING OVER MERIDIAN ADD HA<0 ###

    if pier == 'east' and airmass(alt) < 1.15 and not (alt.degree < 75.0 and 285.0 < az.degree < 300.0) and os.path.isfile(current_file):
        print 'Fine to stay here'
        return

    try:
        sid_current = open(current_file).read().strip()
    except:
        sid_current=None
    print '* STAR HR: ',sid_current

    #get the best objecit
    now = time.localtime()
    yr = now.tm_year
    try:
        sid, ra, dec = hrstar_with_precess.best_star(lst, yr, catalog=catalog, lat=salt_lat)
          #sid, ra, dec = hrstar.best_star(lst,catalog=catalog, lat=salt_lat)
    except ValueError:
        print 'No other acceptable candidates, so best to stay here'
        return

    #get current object
    if sid==sid_current:
        print 'Current object is still best candidate'
        return

    #Move to the new best object
    print 'Slewing to HR %s at RA=%s and Dec=%s' % (sid, ra, dec)
    slew(g, ra, dec)

    #update current value
    if os.path.isfile(current_file): os.remove(current_file)
    fout = open(current_file, 'w')
    fout.write('%s' %sid)
    fout.close()

    try:
        current_star=open('current_object').read().strip()
        print 'HRnr Name    RA2000   Dec2000     Vmag B-V   SED SpType'
        os.system('grep '+str(current_star)+' star.lst')
        os.system('grep '+str(current_star)+' star.lst > current_object_details')
    except:
        print 'Cannot retrieve information from current_object'

    #update the exposure time
    if os.path.isfile(exposure_file): os.remove(exposure_file)
    fout = open(exposure_file, 'w')
    fout.write('3.0e-3')
    fout.close()

if __name__=='__main__':
    with GTO900() as g:
        g.park_off()
        pick_star(g)
