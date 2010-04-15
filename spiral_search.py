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
    os.system("cat spiral.fits | xpaset ds9 fits")
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
    time.sleep(1)
    
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
port.connect('/dev/tty.PL2303-00002006')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

scope.set_slew_centering()
n = 0

has_stars = check_image()

if has_stars:
    print "Got stars right away!"
else:
    while n < 25:
        n = n + 1
        t = n*0.5
        
        minus_y(scope, t)
        print "Going -Y at n = %d and t = %f" % (n, t)
        if check_image():
            break

        plus_x(scope, t)
        print "Going +X at n = %d and t = %f" % (n, t)
        if check_image():
            break

        n = n + 1
        t = n*0.5

        plus_y(scope, t)
        print "Going +Y at n = %d and t = %f" % (n, t)
        if check_image():
            break

        minus_x(scope, t)
        print "Going -X at n = %d and t = %f" % (n, t)
        if check_image():
            break


print "Found stars after %d iterations." % n

time.sleep(1)
port.close()

