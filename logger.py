#!/usr/bin/env python

import logging
import os
from termcolor import colored
 
 
class ColorLog(object):
 
    colormap = dict(
        debug=dict(color='grey', attrs=['bold']),
        info=dict(color='green'),
        warn=dict(color='yellow', attrs=['bold']),
        warning=dict(color='yellow', attrs=['bold']),
        error=dict(color='red'),
        critical=dict(color='red', attrs=['bold']),
    )
 
    def __init__(self, logger):
        self._log = logger
 
    def __getattr__(self, name):
        if name in ['debug', 'info', 'warn', 'warning', 'error', 'critical']:
            return lambda s, *args: getattr(self._log, name)(
                colored(s, **self.colormap[name]), *args)
 
        return getattr(self._log, name)

# Initialize logger
logging.basicConfig(format="%(levelname)s: %(name)s - %(message)s", level=logging.INFO)
fh = logging.FileHandler("%s/ESSS.log" % os.environ['HOME'])
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s - %(name)s - %(message)s"))
