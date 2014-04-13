#!/usr/bin/env python
import os
import hrstar
from pygto900 import GTO900, status, slew

from astropy.coordinates import Angle

def pick_star():
    """A task to check to see if the current star is okay, and if not,
       to find a new star and move to it.
    """

    current_file = 'current_object'
    exposure_file = 'exptime'
    salt_lat=Angle("-32:22:32 degree")
    catalog = 'star.lst'

    g = GTO900()
    g.startup()
    g.clear()
    ra, dec, ha, lst,alt,az,airmass,pier = status(g)
    pier = pier.strip().lower()
    alt = Angle('%s degree' % alt) 
    az = Angle('%s degree' % az) 
  
    if pier == 'e' and airmass < 1.6 and not (alt.degree < 75.0 and 285.0 < az.degree < 300.0) and os.path.isfile(current_file):
       print 'Fine to stay here'
       g.close()
       return

    try:
       sid_current = open(current_file).read().strip()
    except:
       sid_current=None
    print sid_current

    #get the best object
    try:
        sid, ra, dec = hrstar.best_star(lst,catalog=catalog, lat=salt_lat)
    except ValueError:
        print 'No other acceptable candidates, so best to stay here'
        g.close()
        return

    #get current object
    if sid==sid_current:
       print 'Current object is still best candidate'
       g.close()
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
    fout.write('1.0e-3')
    fout.close()
 
    #close connection
    g.close()

if __name__=='__main__':
   pick_star()
