#!/usr/bin/env python

import time
import NexStar
import logger
import logging
import os
import ephem
import timdimm

log = logger.ColorLog(logging.getLogger("Pick Star"))
log.addHandler(logger.fh)

site = timdimm.entoto_site()
cat = timdimm.bright_stars(site)

mag = 10
for star in cat.keys():
    if cat[star].mag < mag:
        mag = cat[star].mag
        brightest = star

log.info("Brightest star is %s at AZ: %s, EL: %s" % (brightest,
                                                     cat[brightest].az,
                                                     cat[brightest].alt))

t = NexStar.NexStar()
t.goto_object(cat[brightest])
time.sleep(1)
while t.goto_in_progress():
    l = t.get_azel()
    log.info("\t Slewing AZ: %s EL: %s..." % (l[0], l[1]))
    time.sleep(1)
log.info("Now on target.")

fp = open("exptime", 'w')
fp.write("1.0e-3\n")
fp.close()

