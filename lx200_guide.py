#!/usr/bin/env python

import time
import sys
import numpy as np
import LX200
from LX200.LX200Utils import *

port = LX200.LXSerial(debug=False)
port.connect('/dev/tty.PL2303-00001004')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

input = open("init_cen_all", 'r')
lines = input.readlines()
input.close()

tol = 80.0

scope.set_slew_centering()

minx = 1000.0
maxx = 0.0
miny = 1000.0
maxy = 0.0

for line in lines:
    x, y = line.split()
    x = float(x)
    y = float(y)
    if x > maxx:
        maxx = x
    if x < minx:
        minx = x
    if y > maxy:
        maxy = y
    if y < miny:
        miny = y

if maxx > 320-tol:
    print "Move East."
    scope.move_East()
if minx < tol:
    print "Move West."
    scope.move_West()
if miny < tol/1.5:
    print "Move North."
    scope.move_North()
if maxy > 240-tol/1.5:
    print "Move South."
    scope.move_South()

time.sleep(0.3)
print "Stop Move."

scope.AbortSlew()
#scope.AbortSlew()
#scope.AbortSlew()
time.sleep(1)

port.close()

