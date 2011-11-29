#!/usr/bin/env python

import sys
import numpy as np
import scipy.ndimage as nd
import pyfits

def rfits(file):
    f = pyfits.open(file, memmap=True)
    hdu = f[0]
    (im, hdr) = (hdu.data, hdu.header)
    f.close()
    return hdu

def daofind(im):
    mean = np.mean(im)
    sig = np.std(im)

    smooth = nd.gaussian_filter(im, 2.0)
    
    clip = smooth >= (mean + 0.6)
    labels, num = nd.label(clip)
    pos = nd.center_of_mass(im, labels, range(num+1))
    print num 
    return num, pos[1:]


if __name__ == '__main__':
    hdu = rfits(sys.argv[1])
    image = hdu.data
    hdr = hdu.header
    n, stars = daofind(image)

    if n == 2:
        print "Found boxes and writing positions."
        output = open("init_cen_all", 'w')
        for star in stars:
            (y, x) = star
            output.write("%8.3f   %8.3f\n" % (x,y))
        output.close()
    else:
        print "No or not enough stars found."
        output = open("init_cen_all", 'w')
        output.write("160.0   120.0\n")
        output.write("198.0   120.0\n")
        output.close()

