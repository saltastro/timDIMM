#!/usr/bin/env python

import sys
import os
import ephem
import time
import numpy as np

salt = ephem.Observer()
salt.lat = "-32:22:32"
salt.lon = "20:48:30"
salt.elevation = 1800
salt.temp = 10
salt.compute_pressure()
salt.epoch=ephem.J2000
salt.date=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

ra = sys.argv[1]
dec = sys.argv[2]

star = ephem.readdb("HR,f|V|A0," + ra + "," + dec + ",10.0,2000")

star.compute(salt)

print star.ra, star.dec, star.alt, star.az
