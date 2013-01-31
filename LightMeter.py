#!/usr/bin/env python

import subprocess
import logger
import logging
import sqlite3 as sql
from threading import Thread

class LightMeter:

    def __init__(self, program='./lightmeter/lightmeter_mark23l'):
        self.program = program
        self.status = False
        self.data = {}
        self.log = logger.ColorLog(logging.getLogger(__name__))
        self.log.addHandler(logger.fh)

    def raw2lux(self, raw):
        return 5.0e-7 * raw

    def stop(self):
        self.status = False

    def runproc(self, prog, l):
        l.info("Starting data acquisition sub-process.")
        p = subprocess.Popen([prog],
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        h1 = p.stdout.readline()
        l.info(h1[2:].strip())
        h2 = p.stdout.readline()
        l.info(h2[2:].strip())
        h3 = p.stdout.readline()

        if h3.find('error') > 0 or h3.find('Error') > 0:
            l.err("ERROR: %s" % h3[2:].strip())
            self.status = False
            return False
        else:
            self.status = True
            l.info(h3[2:].strip())
            data = {}
            con = sql.connect('./lightmeter/lightmeter.db')
            db = con.cursor()
            while self.status:
                line = p.stdout.readline()
                date, time, temp, unit, light, d1, d2, flag, nl = line.split(';')
                data['Date'] = date
                data['time'] = time
                data['T'] = float(temp)
                data['raw'] = int(light)
                data['lux'] = self.raw2lux(data['raw'])
                data['flag'] = flag
                self.data = data
                db.execute("insert into light(temperature, rawdata, lux, flag) \
                values(%f, %d, %f, '%s')" %
                           (data['T'], data['raw'], data['lux'], data['flag']))
                con.commit()
            l.info("Data acquisition stopped.")
            p.terminate()
            con.close()
            return True

    def start(self):
        self.log.info("Starting data acquisition thread.")
        self.t = Thread(target=self.runproc, args=(self.program, self.log))
        self.t.daemon = True
        self.t.start()
        return True
