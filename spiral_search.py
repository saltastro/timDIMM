#!/usr/bin/env python

import os
import time
import sys
import numpy as np
import LX200
from LX200.LX200Utils import *
from find_boxes import *

def check_image():
    os.system("./ave_frames 3 \!spiral.fits")
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

def stop(s):
    s.AbortSlew()
    s.AbortSlew()
    time.sleep(2)
    
def plus_x(s):
    s.move_West()
    time.sleep(0.4)
    stop(s)

def minus_x(s):
    s.move_East()
    time.sleep(0.4)
    stop(s)

def plus_y(s):
    s.move_North()
    time.sleep(0.2)
    stop(s)

def minus_y(s):
    s.move_South()
    time.sleep(0.2)
    stop(s)

port = LX200.LXSerial(debug=False)
port.connect('/dev/tty.PL2303-00001004')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

scope.set_slew_guide()
n = 0
x = 0
y = 0

has_stars = check_image()

if has_stars:
    print "Got stars right away!"
else:
    while n < 50:
        n = n + 1

        for i in range(n):
            y = y - 1
            minus_y(scope)
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break
            time.sleep(1)

        if has_stars:
            break

        for i in range(n):
            x = x + 1
            plus_x(scope)
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break
            time.sleep(1)

        if has_stars:
            break

        n = n + 1

        for i in range(n):
            y = y + 1
            plus_y(scope)
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                stars = True
                break
            time.sleep(1)

        if has_stars:
            break

        for i in range(n):
            x = x - 1
            minus_x(scope)
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                stars = True
                break
            time.sleep(1)

        if has_stars:
            break

print "Found stars after %d iterations." % n

time.sleep(2)
port.close()

