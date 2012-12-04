#!/usr/bin/env python

import time
import sys
import numpy as np
import LX200
from LX200.LX200Utils import *

port = LX200.LXSerial(debug=False)
port.connect('/dev/tty.usbserial')

scope = LX200.Telescope(port, "LX200GPS", debug=False)

alt = from_lx200_angle(scope.get_Altitude())
az = from_lx200_angle(scope.get_AZ())
ra = scope.get_RA()
dec = to_lx200_hms_angle(from_lx200_angle(scope.get_Dec()))
lst = scope.get_sidereal_time()
localtime = scope.get_local_time_24()
airmass = 1.0/np.sin(np.pi*alt/180.0)

ha = to_lx200_hms_angle(from_lx200_angle(lst) - from_lx200_angle(ra))

output = open("lx200.log", "a")
output.write("%s %s %s %s %s %.2f %.2f %.2f\n" % (localtime, lst, ra, dec, ha, alt, az, airmass))
output.close()

port.close()

