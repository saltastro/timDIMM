#!/usr/bin/env python
import os
import hrstar_with_precess_WEST
import hrstar_with_precess
import hrstar
from pygto900 import GTO900, status, slew, airmass
import time

from astropy.coordinates import Angle

def pick_star(g):
    """A task to check to see if the current star is okay, and if not,
       to find a new star and move to it.
    """

    current_file = 'current_object'
    exposure_file = 'exptime'
    salt_lat=Angle("-32:22:32 degree")
    catalog = 'star.lst'

    #ra,dec,ha,lst,alt,az,airmass,pier = status(g)
    alt = Angle('%s degree' % g.alt()) 
    az = Angle('%s degree' % g.az()) 
    pier = g.pier().strip().lower()
    #ha = Angle('%s hour' % g.lst()) - Angle('%s hour' % g.ra())
    ### TO AVOID RUNNING INTO THE PIER WHILE TRACKING OVER MERIDIAN ADD HA<0 ###
  
    if pier == 'east' and airmass(alt) < 1.15 and not (alt.degree < 75.0 and 285.0 < az.degree < 300.0) and os.path.isfile(current_file):
           print 'Fine to stay here'
           return

    try:
       sid_current = open(current_file).read().strip()
    except:
       sid_current=None
    print sid_current

    #get the best object
    try:
       sid, ra, dec = hrstar_with_precess.best_star(g.lst(), 2015, catalog=catalog, lat=salt_lat)
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
    fout.write('%s' % sid)
    fout.close()

    #update the exposure time
    if os.path.isfile(exposure_file): os.remove(exposure_file)
    fout = open(exposure_file, 'w')
    fout.write('3.0e-3')
    fout.close()
    
if __name__=='__main__':
    with GTO900() as g:
       g.park_off()
       pick_star(g)
