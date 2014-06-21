#!/usr/bin/env python

import os
import time
import sys
import numpy as np
from find_boxes import *


def check_image():
    if os.path.isfile("STOP_SPIRAL"): exit()

    os.system("./ave_frames 30 \!spiral.fits")
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
    os.system("./pygto900.py nudge s")


def minus_x():
    os.system("./pygto900.py nudge n")


def plus_y():
    os.system("./pygto900.py nudge e")


def minus_y():
    os.system("./pygto900.py nudge w")



def spiralsearch(niter=100):
   n = 0
   x = 0
   y = 0
   if os.path.isfile("STOP_SPIRAL"): os.remove("STOP_SPIRAL")

   has_stars = check_image()

   if has_stars:
       print "Got stars right away!"
   else:
     while n < niter:
        n = n + 1

        for i in range(n):
            y = y + 1
            plus_y()
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(n)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            x = x - 1
            minus_x()
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(n)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        n = n + 1

        for i in range(n):
            y = y - 1
            minus_y()
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(n)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            x = x + 1
            plus_x()
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(n)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

   return n, x, y


if __name__=='__main__':
   if len(sys.argv)==2:
       niter=int(sys.argv[1])
   else:
       niter=150
   n, x, y = spiralsearch(niter=niter)
   print "Found stars after %d iterations." % n
