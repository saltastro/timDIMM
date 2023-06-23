#!/usr/bin/env python

import logging
import ephem
import numpy as np
import weather as wx
import timdimm
import ox_wagon
from time import sleep

def check_wx(log):
    salt_wx = wx.salt()
    wasp_wx = wx.wasp()
    grav_wx = wx.grav()

    rh = []
    wind = []

    for w in salt_wx, wasp_wx, grav_wx:
        if w:
            rh.append(w['RH'])
            wind.append(w['Wind Speed'])

    mean_rh = np.array(rh).sum()/len(rh)
    mean_wind = np.array(wind).sum()/len(wind)

    if mean_rh > 85:
        log.critical("HUMIDITY LIMIT: %.1f" % mean_rh)
        return "close"
    
    if mean_wind > 55:
        log.critical("WIND LIMIT: %.1f" % mean_wind)
        return "close"

    if salt_wx['Raining'] or wasp_wx['Raining']:
        log.critical("RAIN DETECTED!")
        return "close"

    if mean_rh >= 75 and mean_rh <= 85:
        log.warning("Possible Condensation")
        return "monitor"

    else:
        log.info("Relative Humidity: %.1f" % mean_rh)
        log.info("Wind Speed: %.1f kph" % mean_wind)
        if wasp_wx:
            log.info("Sky: %s" % wasp_wx["Sky"])
        return "open"

def is_it_cloudy():
    wasp = wx.wasp()
    if wasp and wasp['Sky'] == "Clear":
        return False
    else:
        return True

def add_coloring_to_emit_ansi(fn):
    def new(*args):
        levelno = args[1].levelno
        if(levelno >= 50):
            color = '\x1b[31m'  # red
        elif(levelno >= 40):
            color = '\x1b[31m'  # red
        elif(levelno >= 30):
            color = '\x1b[33m'  # yellow
        elif(levelno >= 20):
            color = '\x1b[32m'  # green
        elif(levelno >= 10):
            color = '\x1b[35m'  # pink
        else:
            color = '\x1b[0m'  # normal
        args[1].levelname = color + args[1].levelname + '\x1b[0m'  # normal
        return fn(*args)
    return new

# Initialize logger
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger()

fh = logging.FileHandler("timdimm.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logger.addHandler(fh)

ch = logging.StreamHandler()
f = logging.Formatter("%(levelname)s: %(message)s")
ch.setFormatter(f)
logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)

salt = timdimm.salt_site()
salt.horizon = '0'
sun = ephem.Sun()
moon = ephem.Moon()

while True:
    salt.date = ephem.now()
    sun.compute(salt)
    moon.compute(salt)

    logger.info("Sun Elevation: %s" % sun.alt)
    logger.info("Moon Elevation: %s" % moon.alt)

    if sun.alt < 0:
        logger.info("It's nighttime.")
    else:
        logger.info("It's daytime.")

    if moon.alt > 0:
        logger.info("The moon is up.")
    else:
        logger.info("The moon is down.")

    is_wx_ok = check_wx(logger)

    if is_wx_ok:
        logger.info("The weather is good.")
    else:
        logger.critical("The weather is bad.  Closing...")

    sleep(1)

    
