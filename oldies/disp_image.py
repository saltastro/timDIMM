#!/usr/bin/env python

import os
import time
import sys
import numpy as np
from find_boxes import *
from pygto900 import nudge, GTO900


def check_image():

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


if __name__=='__main__':
   check_image()
