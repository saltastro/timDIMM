#!/usr/bin/env python
from hrstar import load_catalog
from pygto900 import GTO900, slew
from astropy.coordinates import Angle

def goto_hr(current_file='current_object', hr_file='star.lst'):
    """Go to the current object"""

    try:
       sid = open(current_file).read().strip()
    except Exception, e:
       print e
       return 

    #load catalog
    star_dict=load_catalog(hr_file)

    #get ra/dec for best object
    ra = star_dict[sid][1]
    dec = star_dict[sid][2]
    ra = Angle(ra, unit='hour')
    dec = Angle(dec, unit='degree')

    #slew telescope to position
    with GTO900()  as g:
       slew(g, ra, dec)

    
if __name__=='__main__':
   goto_hr()
