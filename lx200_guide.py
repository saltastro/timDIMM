#!/usr/bin/env python

import time
import sys
import numpy as np
import LX200
from LX200.LX200Utils import *

port = LX200.LXSerial(debug=False)
port.connect('/dev/tty.PL2303-00002006')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

input = open("init_cen_all", 'r')
lines = input.readlines()
input.close()

tol = 75.0

scope.set_slew_centering()

for line in lines:
    x, y = line.split()
    x = float(x)
    y = float(y)

    if x > 320-tol:
        print "Move East."
        scope.move_East()
    if x < tol:
        print "Move West."
        scope.move_West()
    if y < tol/1.5:
        print "Move North."
        scope.move_North()
    if y > 240-tol/1.5:
        print "Move South."
        scope.move_South()

time.sleep(0.5)
print "Stop Move."

scope.AbortSlew()
#scope.AbortSlew()
#scope.AbortSlew()
time.sleep(1)

port.close()

