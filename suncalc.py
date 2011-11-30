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
rise = ephem.localtime(salt.next_rising(ephem.Sun())).ctime()
set = ephem.localtime(salt.next_setting(ephem.Sun())).ctime()

if sys.argv[1] == 'rise':
    print rise
else:
    print set
