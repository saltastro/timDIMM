#!/usr/bin/env python

import os
import time
import sys
import numpy as np
from find_boxes import *


def check_image(nframes=30):

    os.system("./ave_frames %i \!temp.fits" % nframes)
    os.system("cat temp.fits | xpaset timDIMM fits")


if __name__=='__main__':
   check_image()
