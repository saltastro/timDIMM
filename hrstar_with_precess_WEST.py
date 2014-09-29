#!/usr/bin/env python

"""
Modified version of hrstar_with_precess.py:
Functions for loading a catalog of stars, determining the RA/DEC for a given
    star, and choosing the best star to observe.
"""
### Modification Log
"""
Created: 2014/06/29 (Laure)
Change the best_star parameters from hrstar_with_precess.py to select stars in West.
This way we avoid the risk of the telescope running into the pier when tracking too long on the same star.
Also changed limiting magnitude from 2.3 to 3.0 and airmass from 1.6 to 1.2 (ie 35 deg from zenith)

"""

import math
from astropy.coordinates import Angle
from astropy.coordinates import FK5
from astropy.time import Time
import astropy.units as u

salt_lat = Angle("-32:22:32 degree")

def Apply_precess(RA,Dec,Year_Now):
    """
    Parameters
    ----------

    Returns
    -------

    """
    Coord_J2000 = FK5('%s %s'%(RA,Dec))
    Coord_NOW = Coord_J2000.precess_to(Time(Year_Now, format='jyear', scale='utc'))
    RA_NOW = Angle(Coord_NOW.ra,unit=u.hour)
    Dec_NOW = Angle(Coord_NOW.dec,unit=u.deg)
    return RA_NOW, Dec_NOW

def load_catalog(catalog='star.lst'):
    """Load a catalog of stars

    Parameters
    ----------

    catalog: string
       Name of catalog with stars in it.  The catalog should have the format of
       id, name (2 columns), rah, ram, ras, ded, dem, des, Vmag, B-V color, and
       Spectral type.

    Returns
    -------
    
    star_dict: dict
       Dictionary with id as key, and containing name, ra, dec, vmag.  ra/dec are 
       astropy.coordinate.angle objects


    """
    #set up the deictionary
    star_dict={}
 
    #read in the catalog
    lines = open(catalog).readlines()

    for l in lines:
      if not l.startswith('#'):
         sid = l[0:4].strip()
         name = l[5:12]
         ra = Angle('%s hour' % (l[13:21]))
         dec = Angle('%s%s degree' % (l[22], l[24:32]))
         vmag = float(l[34:38])
         star_dict[sid] = [name, ra, dec, vmag]
    return star_dict

def calculate_airmass(ha, dec, lat=salt_lat):
   """Calculate the airmass given an hour angle and declination

    Parameters
    ----------

    ha: astropy.coordinates.Angle
       Hour angle for an object

    dec: astropy.coordinates.Angle
       declination for an object

    lat: astropy.coordinates.Angle
       Latitude of the observatory

    Returns
    -------
    az: astropy.coordinates.Angle
       Azimuth of source

    alt: astropy.coordinates.Angle
       Altitude of source

    airmass: float
       Airmass of source

   """
   #calculate the altitude
   alt = math.sin(dec.radian)*math.sin(lat.radian) + \
          math.cos(dec.radian)*math.cos(lat.radian)*math.cos(ha.radian)
   alt = math.asin(alt)
   alt = Angle(alt, unit='radian')

   if lat.degree == 0 or alt.degree == 0:
       az = 0
   else:
       n = -1.0*math.sin(ha.radian)
       d = -1.0*math.cos(ha.radian) * math.sin(lat.radian) + \
           math.sin(dec.radian) * math.cos(lat.radian) / math.cos(dec.radian)
       az = math.atan2(n,d)
       if az < 0: az += 2*math.pi
   az = Angle(az, unit='radian')   

   ang = Angle(90, unit='degree') - alt
   airmass = 1.0 / math.cos(ang.radian)
   return az, alt, airmass
 

def best_star(lst, Year_NOW, star_dict=None, catalog=None, lat=salt_lat):
    """Given an lst and a catalog of stars, determine the best star in the list.
       The best star is determined to have an airmass less than 1.2, a
       magnitude below 3.0, and an hour angle greater than 0.5. And we will pic
       it to be in the West to avoid running into the pier while tracking
       (55<Alt<90  and  181<Az<359).

       This is specific to the current position of the timdimm in the ox-wagon
       and should be updated if the telescope is moved

    Parameters
    ----------

    lst: string
       The local sideral time

    star_dict: dict
       Dictionary with id as key, and containing name, ra, dec, vmag.  ra/dec are 
       astropy.coordinate.angle objects

    catalog: string 
       Name of catalog with stars in it.  The catalog should have the format of
       id, name (2 columns), rah, ram, ras, ded, dem, des, Vmag, B-V color, and
       Spectral type.  Only uses catalog if star_dict is None

    Returns
    -------
    
    sid: string
       key for object in star_dict

    ra: astropy.coordinates.Angle
       RA for best star 

    dec: astropy.coordinates.Angle
       Declination for best star 

    Exceptions
    ----------

    Raises ValueError if no star acceptable star exists

    """
    if star_dict is None:
       star_dict = load_catalog(catalog)

    best_sid = None
    best_vmag = 99
    for k in star_dict.keys():
        ra = star_dict[k][1]
        dec = star_dict[k][2]
        RA_now, Dec_now = Apply_precess(ra,dec,Year_NOW)
        vmag = star_dict[k][3]
        ha = Angle('%s hour' % lst) - RA_now
        az, alt, airmass = calculate_airmass(ha, Dec_now, lat=lat)

        if ha.degree > 0.5 and  vmag < 3.0 and vmag < best_vmag and alt.degree > 55.0 and 181.0 < az.degree < 359.0:
          best_sid = k
          best_vmag = vmag
          best_RA = Apply_precess(star_dict[best_sid][1], star_dict[best_sid][2],Year_NOW)[0]
          best_Dec = Apply_precess(star_dict[best_sid][1], star_dict[best_sid][2],Year_NOW)[1]

    if best_sid is None:
       raise ValueError('No acceptable stars found')

    # Suppress decimal values and min/sec = 60
    h_RA = int(best_RA.hms[0])
    m_RA = int(best_RA.hms[1])
    if m_RA == 60:
       h_RA = int(h_RA+1)
       m_RA = '00'
    s_RA = int(round(best_RA.hms[2]))
    if s_RA == 60:
       m_RA = int(m_RA+1)
       s_RA = '00'
    d_Dec = int(best_Dec.dms[0])
    m_Dec = abs(int(best_Dec.dms[1]))
    if m_Dec == 60:
       d_Dec = int(d_Dec+1)
       m_Dec = '00'
    s_Dec = abs(int(round(best_Dec.dms[2])))
    if s_Dec == 60:
       m_Dec = int(m_Dec+1)
       s_Dec = '00'

    return best_sid, Angle('%s:%s:%s hour'%(h_RA,m_RA,s_RA)), Angle('%s:%s:%s degree'%(d_Dec,m_Dec,s_Dec))

#lst = '12:30:30'
#print best_star(lst, catalog='star.lst')

if __name__=='__main__':
   import sys
   sid,ra,dec=best_star(sys.argv[1],int(sys.argv[2]), catalog='star.lst')
   print sid, ra, dec
