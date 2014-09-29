#!/usr/bin/env python

import os
import time
import sys
import numpy as np
from find_boxes import *
from pygto900 import nudge, GTO900


def check_image():
    if os.path.isfile("STOP_SPIRAL"): 
       return -1, 0, 0

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


def plus_x(g):
    nudge(g, 's')


def minus_x(g):
    nudge(g, 'n')


def plus_y(g):
    nudge(g, 'e')


def minus_y(g):
    nudge(g, 'w')


def spiralsearch(g, niter=150):
   n = 0
   x = 0
   y = 0
   it = 0
   if os.path.isfile("STOP_SPIRAL"): os.remove("STOP_SPIRAL")

   has_stars = check_image()

   if has_stars:
       print "Got stars right away!"
   else:
     while n < niter:
        n = n + 1

        for i in range(n):
            it = it + 1
            y = y + 1
            plus_y(g)
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(it)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            it = it + 1
            x = x - 1
            minus_x(g)
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(it)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        n = n + 1

        for i in range(n):
            it = it + 1
            y = y - 1
            minus_y(g)
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(it)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

        for i in range(n):
            it = it + 1
            x = x + 1
            plus_x(g)
            print "At (x, y) = (%d, %d)" % (x, y)
            print "Iteration: %s" %(it)
            if check_image():
                has_stars = True
                break

        if has_stars:
            break

   if has_stars: return n, x, y
   return -1, x, y


if __name__=='__main__':
   if len(sys.argv)==2:
       niter=int(sys.argv[1])
   else:
       niter=15

   with GTO900() as g:
       n, x, y = spiralsearch(g, niter=niter)
       g.park_mode()
   print "Found stars after %d iterations." % n
