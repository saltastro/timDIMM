#!/usr/bin/env python

import os
import time
import sys
import numpy as np
from find_boxes import *

def check_image():
    os.system("./ave_frames 10 \!spiral.fits")
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

def plus_x():
    os.system("./gto900_nudge.rb s")

def minus_x():
    os.system("./gto900_nudge.rb n")

def plus_y():
    os.system("./gto900_nudge.rb e")

def minus_y():
    os.system("./gto900_nudge.rb w")

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
            y = y + 1
            plus_y()
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            x = x - 1
            minus_x()
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        n = n + 1

        for i in range(n):
            y = y - 1
            minus_y()
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            x = x + 1
            plus_x()
            print "At (x,y) = (%d,%d)" % (x,y)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break


print "Found stars after %d iterations." % n
