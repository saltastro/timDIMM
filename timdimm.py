#!/usr/bin/env python

import re
import ephem
import numpy as np

# return airmass for ephem.Object
def airmass(alt):
    if alt > 0.0:
	secz = 1/np.cos(ephem.degrees('90:00:00') -
                        ephem.degrees(alt))
    else:
	secz = 999.0
    return secz

# set up ephem Observer for the SALT site
def salt_site():
    salt = ephem.Observer()
    salt.lat = "-32:22:32"
    salt.long = "20:48:30"
    salt.elevation = 1800
    salt.temp = 10
    salt.compute_pressure()
    salt.horizon = '-12'
    salt.date = ephem.now()
    return salt

# set up ephem Observer for the entoto site
def entoto_site():
    site = ephem.Observer()
    site.lat = "+09:06:28.14"
    site.long = "38:48:29.42"
    site.elevation = 3174
    site.temp = 10
    site.compute_pressure()
    site.horizon = '-12'
    site.date = ephem.now()
    return site

# read in xephem's sky 2k catalog
def sky2k_catalog(site=None):
    fp = open("/opt/local/share/xephem/catalogs/SKY2k65.edb")
    lines = fp.readlines()
    fp.close()
    stars = {}

    p = re.compile('#')
    for line in lines:
        if not p.match(line):
            obj = ephem.readdb(line)
            names = obj.name.split('|')
            for name in names:
                stars[name] = obj
                if site:
                    stars[name].compute(site)
    return stars

# cull xephem's catalog to only include bright stars
def bright_stars(site=None):
    fp = open("/opt/local/share/xephem/catalogs/SKY2k65.edb")
    lines = fp.readlines()
    fp.close()
    stars = {}

    p = re.compile('#')
    for line in lines:
        if not p.match(line):
            obj = ephem.readdb(line)
            if site:
                obj.compute(site)
                if obj.mag < 2.0 and obj.alt > ephem.degrees("30:00:00"):
                    names = obj.name.split('|')
                    stars[names[0]] = obj
    return stars

# read in HR catalog list used by turbina
def hr_catalog(site=None):
    fp = open("star.lst", "r")
    lines = fp.readlines()
    fp.close()
    stars = {}

    p = re.compile('#')
    for line in lines: 
        if not p.match(line):
            hr = line[0:4].strip()
            name = line[5:12]
            h = line[13:15]
            m = line[16:18]
            s = line[19:21]
            ra = "%s:%s:%s" % (h, m, s)

            sign = line[22:23]
            d = line[24:26]
            m = line[27:29]
            s = line[30:32]
            dec = "%s%s:%s:%s" % (sign, d, m, s)
	 
            vmag = float(line[33:38])
            bmv = float(line[39:44])
            sed = line[45:48]
            sptype = line[49:63]
            dbstr = "%s,f|S|%s,%s,%s,%f,2000" % (name, sptype, ra, dec, vmag)
            stars[hr] = ephem.readdb(dbstr)
	    if site:
		stars[hr].compute(site)
    return stars

def best_star(site):
    cat = hr_catalog(site)
    good = []

    for key,star in cat.items():
        lst = site.sidereal_time()
        ha = ephem.hours(lst - star.ra)
        if ha > 0.02 and airmass(star) < 1.6 and star.mag < 2.8:
	    good.append(key)

    good.sort(lambda x, y: cmp(cat[x].mag, cat[y].mag))
    return good
        

def vis_strip():
    site = salt_site()
    cat = hr_catalog(site)
    good = []
    upper = ephem.degrees('65.0')
    lower = ephem.degrees('43.0')
    
    for key,star in cat.items():
	lst = site.sidereal_time()
	ha = ephem.hours(lst - star.ra)
	
	if star.alt < upper and star.alt > lower:
	    good.append(key)

    good.sort(lambda x, y: cmp(cat[x].mag, cat[y].mag))
    return good
