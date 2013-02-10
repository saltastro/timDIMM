#!/usr/bin/env python

import NexStar
import logger
import logging
import os
import numpy as np
from timdimm import airmass

pixscale = 1.05

log = logger.ColorLog(logging.getLogger("DIMM"))
log.addHandler(logger.fh)

t = NexStar.NexStar()

while True:
    (az, el) = t.get_azel()
    secz = airmass(el)
    log.info("Measuring seeing at AZ: %s, EL: %s, AIRMASS: %.2f" % (az, el, secz))
    if secz > 2.0:
        log.warn("Star too low. Please pick another.")
    os.system("./timdimm.sh %f" % secz)
    x, y = np.loadtxt("init_cen_all", unpack=True)
    dx = x.mean() - 80.0
    dy = y.mean() - 120.0
    if dx < -25.0:
        log.info("Star too far to left, moving right...")
        t.nudge("Right", 3)
    if dx > 25.0:
        log.info("Star too far to right, moving left...")
        t.nudge("Left", 3)
    if dy > 30.0:
        log.info("Star too high, moving down...")
        t.nudge("Down", 3)
    if dy < -30.0:
        log.info("Star too low, moving up...")
        t.nudge("Up", 3)
