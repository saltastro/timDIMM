#!/usr/bin/env python

import sys
import numpy as np
import scipy.ndimage as nd
import pyfits
import imagestats
from find_boxes import *

pixel_scale = 1.22
rd = 0.13
d = 0.06
lamb = 0.65e-6

def seeing(v):
    b = rd/d
    v = v*(pixel_scale/206265.0)**2.0
    k = 0.364*(1.0 - 0.532*b**(-1.0/3.0) - 0.024*b**(-7.0/3.0))
    seeing = 206265.0*0.98*( (d/lamb)**0.2 )*( (v/k)**0.6 )
    return seeing

def old_seeing(v):
    v = v*(pixel_scale/206265.0)**2.0
    r0 = ( 2.0*lamb*lamb*( 0.1790*(d**(-1.0/3.0)) - 0.0968*(rd**(-1.0/3.0)) )/v )**0.6
    seeing = 206265.0*0.98*lamb/r0;
    return seeing

hdu = rfits(sys.argv[1])
image = hdu.data
hdr = hdu.header

x1 = []
y1 = []
c1 = []

x2 = []
y2 = []
c2 = []

for i in range(image.shape[0]):
    n, test = daofind(image[i])
    if n == 2:
        x1.append(test[0][0])
        y1.append(test[0][1])
        x2.append(test[1][0])
        y2.append(test[1][1])

x1 = np.array(x1)
x2 = np.array(x2)
y1 = np.array(y1)
y2 = np.array(y2)

r = np.sqrt( (x2-x1)**2 + (y2-y1)**2 )
var = np.var(r)

print "Var = %f, Seeing = %f, Old Seeing = %f" % (float(var), float(seeing(var)), float(old_seeing(var)))



