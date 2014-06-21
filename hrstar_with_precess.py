#!/usr/bin/env python

"""Functions for loading a catalog of stars, determining the RA/DEC for a given
    star, and choosing the best star to observe.
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

    Note
    ----

    Convert J2000 coordinates to NOW

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
       The best star is determined to have an airmass less than 1.6, a
       magnitude below 2.3, and an hour angle greater than 0.5.

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
        if ha.degree < 0.5 and 0 < airmass < 1.6 and vmag < 2.3 and vmag < best_vmag:
          if not (alt.degree < 75.0 and 285.0 < az.degree < 300.0):
             best_sid = k
             best_vmag = vmag
             best_RA = Apply_precess(star_dict[best_sid][1], star_dict[best_sid][2],Year_NOW)[0]
             best_Dec = Apply_precess(star_dict[best_sid][1], star_dict[best_sid][2],Year_NOW)[1]

    if best_sid is None:
       raise ValueError('No acceptable stars found')
    h_RA = int(best_RA.hms[0])
    m_RA = int(best_RA.hms[1])
    s_RA = int(round(best_RA.hms[2]))
    d_Dec = int(best_Dec.dms[0])
    m_Dec = abs(int(best_Dec.dms[1]))
    s_Dec = abs(int(round(best_Dec.dms[2])))

    return best_sid, Angle('%s:%s:%s hour'%(h_RA,m_RA,s_RA)), Angle('%s:%s:%s degrees'%(d_Dec,m_Dec,s_Dec))

#lst = '12:30:30'
#print best_star(lst, catalog='star.lst')

if __name__=='__main__':
   import sys
   sid,ra,dec=best_star(sys.argv[1],int(sys.argv[2]), catalog='star.lst')
   print sid, ra, dec
