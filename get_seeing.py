#!/usr/bin/env python

import NexStar
import logger
import logging
import os
from timdimm import airmass


log = logger.ColorLog(logging.getLogger(__name__))
log.addHandler(logger.fh)

t = NexStar.NexStar()

while True:
    (az, el) = t.get_azel()
    secz = airmass(el)
    log.info("Measuring seeing at AZ=%s, EL=%s, AIRMASS=%.2f" % (az, el, secz))
    os.system("./timdimm.sh %f" % secz)
    
