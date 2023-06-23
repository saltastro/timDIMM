#!/usr/bin/env python

import sys
import os
import ephem
import numpy as np
import sys

salt = ephem.Observer()
salt.lat = "-32:22:32"
salt.long = "20:48:30"
salt.elevation = 1800
salt.temp = 10
salt.compute_pressure()
salt.horizon = '-12'
sun = ephem.Sun()

sun.compute(salt)
print float(sun.alt)*180.0/np.pi

rise = ephem.localtime(salt.next_rising(sun))
set = ephem.localtime(salt.next_setting(sun))

now = ephem.localtime(ephem.now())

salt.date = ephem.now()

print "LST: %s" % salt.sidereal_time()

t2rise = rise-now
t2set = set-now

print "12 degree evening twilight ends in ", t2set
print "12 degree morning twilight begins in ", t2rise

print "Morning twilight: ", rise.ctime()

print "Evening twilight: ", set.ctime()
