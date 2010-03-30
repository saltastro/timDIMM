#!/usr/bin/env python

import sys
import numpy as np
import matplotlib
import matplotlib.ticker as ticker
import maplotlib.dates as dates
import datetime

from LX200 import *

def format_time(x, pos=None):
    return dates.num2date(x).strftime('%H:%M')

port = LXSerial(debug=True)
port.connect('/dev/tty.PL2303')
scope = Telescope(port, "LX200", debug=True)

scope.set_slew_rate(GUIDE)

