#!/usr/bin/env python

import os
import time
import sys
import numpy as np
import LX200
from LX200.LX200Utils import *
from find_boxes import *

def check_image():
    os.system("./ave_frames 5 \!spiral.fits")
    os.system("cat spiral.fits | xpaset timDIMM fits")
    hdu = rfits("spiral.fits")
    image = hdu.data
    n, stars = daofind(image)
    
    if n == 2:
        print "Found the stars!"
        return True
    else:
        print "No dice."
        return False

def stop(s, t):
    time.sleep(t)
    s.AbortSlew()
    s.AbortSlew()
    time.sleep(2)
    
def plus_x(s, t):
    s.move_West()
    stop(s, t)

def minus_x(s, t):
    s.move_East()
    stop(s, t)

def plus_y(s, t):
    s.move_North()
    stop(s, t)

def minus_y(s, t):
    s.move_South()
    stop(s, t)

port = LX200.LXSerial(debug=False)
port.connect('/dev/tty.PL2303-00001004')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

scope.set_slew_guide()
n = 0
t = 0.0

has_stars = check_image()

if has_stars:
    print "Got stars right away!"
else:
    while n < 50:
        n = n + 1
        t = t + 0.3
        
        minus_y(scope, t)
        print "Going -Y at n = %d and t = %f" % (n, t)
        if check_image():
            break
        time.sleep(1)
        plus_x(scope, t)
        print "Going +X at n = %d and t = %f" % (n, t)
        if check_image():
            break
        time.sleep(1)
        n = n + 1
        t = t + 0.3

        plus_y(scope, t)
        print "Going +Y at n = %d and t = %f" % (n, t)
        if check_image():
            break
        time.sleep(1)
        minus_x(scope, t)
        print "Going -X at n = %d and t = %f" % (n, t)
        if check_image():
            break
        time.sleep(1)

print "Found stars after %d iterations." % n

time.sleep(2)
port.close()

