#!/usr/bin/env python
"""
            NexStar

A collection of classes and functions that implements Celestron's
NexStar communication protocol. The information is gleaned from the
document 1154108406_nexstarcommprot.pdf.

Author                     Version             Date
--------------------------------------------------------
TE Pickering                 0.1             20121126

TODO
--------------------------------------------------------

Updates
--------------------------------------------------------

"""

import time
import serial
import ephem
import datetime
import struct
import logger
import logging


class NexStar:
    """
    main class to encapsulate NexStar interface and operation
    """

    tracking_modes = ["Off", "Alt/Az", "EQ North", "EQ South"]
    devices = {"AZ/RA Motor": 16, "ALT/DEC Motor": 17,
               "GPS Unit": 176, "RTC": 178}
    models = ["", "GPS Series", "", "i-Series", "i-Series SE", "CGE",
              "Advanced GT", "SLT", "", "CPC", "GT", "4/5 SE", "6/8 SE"]
    variable_slew = {"Right": (16, 6), "Left": (16, 7),
                     "Up": (17, 6), "Down": (17, 7)}
    fixed_slew = {"Right": (16, 36), "Left": (16, 37),
                  "Up": (17, 36), "Down": (17, 37)}

    def __init__(self, port="/dev/tty.usbserial-AH01GROD"):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 9600
        self.ser.timeout = 3.5
        self.ser.open()
        self.log = logger.ColorLog(logging.getLogger(__name__))
        self.log.addHandler(logger.fh)

    def hex2ang(self, s, hours=False, precise=True):
        """
        the NexStar returns either a 16 or 32-bit hex number denoting
        the angle in revolutions
        """
        i = int("0x%s" % s, 16)
        if precise:
            rev = i / 4294967296.0
        else:
            rev = i / 65536.0
        if hours:
            return ephem.hours(rev * 2.0 * ephem.pi)
        else:
            return ephem.degrees(rev * 2.0 * ephem.pi)

    def ang2hex(self, a, precise=True):
        """
        take an angle in radians (which ephem provides by default) and convert
        to hex to send on to the NexStar
        """
        rev = a.norm / (2.0 * ephem.pi)
        if precise:
            resp = "%08x" % int(rev * 4294967296)
            return resp.upper()
        else:
            resp = "%04x" % int(rev * 65536)
            return resp.upper()

    def get_radec(self, precise=True):
        """
        read the current RA/Dec
        """
        if precise:
            self.ser.write("e")
            resp = self.ser.read(18)
            ra = resp[0:8]
            dec = resp[9:17]
        else:
            self.ser.write("E")
            resp = self.ser.read(10)
            ra = resp[0:4]
            dec = resp[5:9]
        return (self.hex2ang(ra, hours=True, precise=precise),
                self.hex2ang(dec, precise=precise))

    def get_azel(self, precise=True):
        """
        read the current Az-El
        """
        if precise:
            self.ser.write("z")
            resp = self.ser.read(18)
            az = resp[0:8]
            el = resp[9:17]
        else:
            self.ser.write("Z")
            resp = self.ser.read(10)
            az = resp[0:4]
            el = resp[5:9]
        return (self.hex2ang(az, precise=precise),
                self.hex2ang(el, precise=precise))

    def goto_radec(self, ra, dec, precise=True):
        """
        slew to RA, Dec
        """
        ra = ephem.hours(ra)
        dec = ephem.degrees(dec)
        if precise:
            cmd = 'r'
        else:
            cmd = 'R'
        full_cmd = "%s%s,%s" % (cmd,
                                self.ang2hex(ra, precise=precise),
                                self.ang2hex(dec, precise=precise))
        self.ser.write(full_cmd)
        resp = self.ser.read(1)
        if resp == '#':
            self.log.info("Slewing to RA=%s, Dec=%s...." % (ra, dec))
            self.log.info("\t raw command: %s" % full_cmd)
            return True
        else:
            self.log.error("Error in slew command...")
            resp = self.ser.read(1)
            return False

    def goto_object(self, obj):
        """
        take ephem object and slew to it
        """
        self.goto_radec(obj.ra, obj.dec, precise=True)

    def goto_azel(self, az, el, precise=True):
        """
        slew to Az, El
        """
        az = ephem.degrees(az)
        el = ephem.degrees(el)
        if precise:
            cmd = 'b'
        else:
            cmd = 'B'
        full_cmd = "%s%s,%s" % (cmd,
                                self.ang2hex(az, precise=precise),
                                self.ang2hex(el, precise=precise))
        self.ser.write(full_cmd)
        resp = self.ser.read(1)
        if resp == '#':
            self.log.info("Slewing to Az=%s, El=%s...." % (az, el))
            return True
        else:
            self.log.error("Error in slew command...")
            resp = self.ser.read(1)
            return False

    def sync(self, ra, dec, precise=True):
        """
        sync NexStar to provided RA and Dec
        """
        if precise:
            cmd = 's'
        else:
            cmd = 'S'
        full_cmd = "%s%s,%s" % (cmd,
                                self.ang2hex(ra, precise=precise),
                                self.ang2hex(dec, precise=precise))
        self.ser.write(full_cmd)
        resp = self.ser.read(1)
        if resp == '#':
            self.log.info("Syncing mount to RA=%s, Dec=%s...." % (ra, dec))
            return True
        else:
            self.log.error("Error in sync command...")
            resp = self.ser.read(1)
            return False

    def get_tracking_mode(self):
        """
        query mount for current tracking mode
        """
        self.ser.write("t")
        resp = self.ser.read(2)
        mode, c = struct.unpack("BB", resp)
        if mode in range(4):
            self.log.info("Current tracking mode is: %s" %
                          NexStar.tracking_modes[mode])
            return mode
        else:
            self.log.error("Error querying tracking mode.")
            return None

    def set_tracking_mode(self, mode):
        """
        set mount's tracking mode
        """
        assert mode in range(4), "Mode must be integer in range 0-3."
        cmd = "T" + chr(mode)
        self.ser.write(cmd)
        resp = self.ser.read(1)
        if resp == '#':
            self.log.info("Successfully set tracking mode to: %s" %
                          NexStar.tracking_modes[mode])
            return True
        else:
            self.log.error("Error setting tracking mode.")
            return False

    def set_slew_rate(self, rate, dir, fixed=True):
        """
        set the mount's slew rate.  fixed takes a range of 0-9 with 0 being
        stop. the values mimic the hand control rates. otherwise the rate
        is given in arcseconds/second.
        """
        if fixed:
            assert rate in range(10), "Fixed slew rates must be in range 0-9."
            assert dir in NexStar.fixed_slew.keys(), \
                "Direction must be one of Up, Down, Right, Left."
            if rate > 0:
                self.log.info("Moving %s at fixed rate %d." % (dir, rate))
            else:
                self.log.info("Stopping %s-ward motion." % dir)
            vals = NexStar.fixed_slew[dir]
            cmd = "P" + chr(2) + chr(vals[0]) + chr(vals[1]) \
                + chr(rate) + chr(0) + chr(0) + chr(0)
            self.ser.write(cmd)
            resp = self.ser.read(1)
            if resp != '#':
                self.ser.read(1)
                self.log.error("Error setting slew rates: %s" % resp)
                return False
        else:
            assert rate >= 0, 'Slew rate must be >= 0!'
            assert dir in NexStar.variable_slew.keys(), \
                "Direction must be one of Up, Down, Right, Left."
            if rate > 0:
                self.log.info("Moving %s at variable rate of %d arcsec/sec." %
                              (dir, rate))
            else:
                self.log.info("Stopping %s-ward motion." % dir)
            vals = NexStar.variable_slew[dir]
            rateHigh = (int(rate) * 4) / 256
            rateLow = (int(rate) * 4) % 256
            cmd = "P" + chr(3) + chr(vals[0]) + chr(vals[1]) \
                + chr(rateHigh) + chr(rateLow) + chr(0) + chr(0)
            self.ser.write(cmd)
            resp = self.ser.read(1)
            if resp != '#':
                self.ser.read(1)
                self.log.error("Error setting slew rates.")
                return False
        return True

    def get_location(self):
        """
        query the location from the handset (NOT the GPS).
        read into a-h variables to follow document.
        """
        self.ser.write('w')
        resp = self.ser.read(9)
        a, b, c, d, e, f, g, h = [ord(ch) for ch in resp[0:-1]]
        if d == 0:
            latsign = "+"
        else:
            latsign = "-"
        if h == 0:
            lonsign = "+"
        else:
            lonsign = "-"
        lat = "%s%2d:%02d:%02d" % (latsign, a, b, c)
        lon = "%s%3d:%02d:%02d" % (lonsign, e, f, g)
        self.log.info("Current mount location: Lat=%s, Lon=%s" % (lat, lon))
        return ephem.degrees(lat), ephem.degrees(lon)

    def get_time(self):
        """
        query the time from the handset (NOT the GPS).
        read into q-x variables to follow document
        """
        self.ser.write('h')
        resp = self.ser.read(9)
        q, r, s, t, u, v, w, x = [ord(ch) for ch in resp[0:-1]]
        if w > 128:
            w -= 256
        time = "20%02d-%02d-%02d %d:%02d:%02d UTC%+2d" % (v, t, u, q, r, s, w)
        self.log.info("Current mount time: %s" % time)
        return time

    def set_location(self, lat, lon):
        """
        set the handset location
        """
        if lat >= 0:
            d = 0
        else:
            d = 1
        if lon >= 0:
            h = 0
        else:
            h = 1
        a, b, c = str(lat).split(':')
        a = a.replace('+', '').replace('-', '')
        c = c.split('.')[0]
        e, f, g = str(lon).split(':')
        e = e.replace('+', '').replace('-', '')
        g = g.split('.')[0]
        cmd = "W" + chr(a) + chr(b) + chr(c) + chr(d) + \
            chr(e) + chr(f) + chr(g) + chr(h)
        self.log.info("Setting mount location to Lat=%s, Lon=%s." % (lat, lon))
        self.ser.write(cmd)
        resp = self.ser.read(1)
        if resp != '#':
            self.ser.read(1)
            self.log.error("Error setting current location.")
            return False
        return True

    def set_time(self):
        """
        configure handset to use current universal time
        """
        t = datetime.datetime.utcnow()
        w = 0
        x = 0
        q = t.hour
        r = t.minute
        s = t.second
        tm = t.month
        u = t.day
        v = t.year - 2000
        cmd = "H" + chr(q) + chr(r) + chr(s) + chr(tm) + \
            chr(u) + chr(v) + chr(w) + chr(x)
        self.log.info("Setting mount time to %s UTC" %
                      t.strftime("%Y-%m-%d %H:%M:%S"))
        self.ser.write(cmd)
        time.sleep(2)
        resp = self.ser.read(1)
        if resp != '#':
            self.ser.read(1)
            self.log.info("Error setting current time.")
            return False
        return True

    def is_gps_linked(self):
        """
        check if the GPS unit in the NexStar mount is linked.
        """
        cmd = "P" + chr(1) + chr(176) + chr(55) + chr(0) + \
            chr(0) + chr(0) + chr(1)
        self.ser.write(cmd)
        resp = self.ser.read(2)
        x = ord(resp[0])
        if x > 0:
            self.log.info("Mount GPS is linked.")
            return True
        else:
            self.log.info("Mount GPS is not linked.")
            return False

    def get_gps_latitude(self):
        """
        query GPS unit for current latitude
        """
        cmd = "P" + chr(1) + chr(176) + chr(1) + chr(0) + \
            chr(0) + chr(0) + chr(3)
        self.ser.write(cmd)
        resp = self.ser.read(4)
        x = ord(resp[0])
        y = ord(resp[1])
        z = ord(resp[2])
        lat = (x * 65536.0 + y * 256.0 + z) / 2 ** 24
        lat = ephem.degrees(2.0 * ephem.pi * lat).znorm
        self.log.info("Current mount latitude from GPS: %s" % lat)
        return lat

    def get_gps_longitude(self):
        """
        query GPS unit for current longitude
        """
        cmd = "P" + chr(1) + chr(176) + chr(2) + chr(0) + \
            chr(0) + chr(0) + chr(3)
        self.ser.write(cmd)
        resp = self.ser.read(4)
        x = ord(resp[0])
        y = ord(resp[1])
        z = ord(resp[2])
        lon = (x * 65536.0 + y * 256.0 + z) / 2 ** 24
        lon = ephem.degrees(2.0 * ephem.pi * lon).znorm
        self.log.info("Current mount longitude from GPS: %s" % lon)
        return lon

    def get_gps_time(self):
        """
        query GPS unit for the current time
        """
        # first get the date
        cmd = "P" + chr(1) + chr(176) + chr(3) + chr(0) + \
            chr(0) + chr(0) + chr(2)
        self.ser.write(cmd)
        resp = self.ser.read(3)
        month = ord(resp[0])
        day = ord(resp[1])

        # now get the year
        cmd = "P" + chr(1) + chr(176) + chr(4) + chr(0) + \
            chr(0) + chr(0) + chr(2)
        self.ser.write(cmd)
        resp = self.ser.read(3)
        x = ord(resp[0])
        y = ord(resp[1])
        year = x * 256 + y

        # and now get the time
        cmd = "P" + chr(1) + chr(176) + chr(51) + chr(0) + \
            chr(0) + chr(0) + chr(3)
        self.ser.write(cmd)
        resp = self.ser.read(4)
        hour = ord(resp[0])
        minute = ord(resp[1])
        second = ord(resp[2])
        d = ephem.Date("%d/%02d/%02d %d:%02d:%02d" %
                      (year, month, day, hour, minute, second))
        self.log.info("Current mount time from GPS: %s" % d)
        return d

    def get_rtc_time(self):
        """
        query mount's RTC unit for the current time
        """
        # first get the date
        cmd = "P" + chr(1) + chr(178) + chr(3) + chr(0) + \
            chr(0) + chr(0) + chr(2)
        self.ser.write(cmd)
        resp = self.ser.read(3)
        month = ord(resp[0])
        day = ord(resp[1])

        # now get the year
        cmd = "P" + chr(1) + chr(178) + chr(4) + chr(0) + \
            chr(0) + chr(0) + chr(2)
        self.ser.write(cmd)
        resp = self.ser.read(3)
        x = ord(resp[0])
        y = ord(resp[1])
        year = x * 256 + y

        # and now get the time
        cmd = "P" + chr(1) + chr(178) + chr(51) + chr(0) + \
            chr(0) + chr(0) + chr(3)
        self.ser.write(cmd)
        resp = self.ser.read(4)
        hour = ord(resp[0])
        minute = ord(resp[1])
        second = ord(resp[2])
        d = ephem.Date("%d/%02d/%02d %d:%02d:%02d" %
                      (year, month, day, hour, minute, second))
        self.log.info("Current mount time from the RTC: %s" % d)
        return d

    def set_rtc_time(self, t):
        """
        set the time in the mount's RTC unit. takes datetime object as
        argument
        """
        self.log.info("Setting mount RTC time to %s UTC" %
                      t.strftime("%Y-%m-%d %H:%M:%S"))
        # first set the date
        cmd = "P" + chr(3) + chr(178) + chr(131) + chr(t.month) + \
            chr(t.day) + chr(0) + chr(0)
        self.ser.write(cmd)
        self.ser.read(1)

        # now set the year
        x = t.year / 256
        y = t.year % 256
        cmd = "P" + chr(3) + chr(178) + chr(132) + chr(x) + \
            chr(y) + chr(0) + chr(0)
        self.ser.write(cmd)
        self.ser.read(1)

        # and now set the time
        cmd = "P" + chr(3) + chr(178) + chr(132) + chr(t.hour) + \
            chr(t.minute) + chr(t.second) + chr(0)
        self.ser.write(cmd)
        self.ser.read(1)
        return True

    def get_version(self):
        """
        get telescope version
        """
        self.ser.write("V")
        resp = self.ser.read(3)
        version = "%d.%d" % (ord(resp[0]), ord(resp[1]))
        self.log.info("Mount version is %s" % version)
        return version

    def get_device_versions(self):
        """
        query versions for the specific components of the telescope
        """
        versions = {}
        self.log.info("Querying versions for telescope components:")
        for k, v in NexStar.devices.items():
            cmd = "P" + chr(1) + chr(v) + chr(254) + chr(0) + \
                chr(0) + chr(0) + chr(2)
            self.ser.write(cmd)
            resp = self.ser.read(3)
            version = "%d.%d" % (ord(resp[0]), ord(resp[1]))
            self.log.info("\t %s => %s" % (k, version))
            versions[k] = version
        return versions

    def get_model(self):
        """
        query telescope model
        """
        self.ser.write("m")
        resp = self.ser.read(2)
        i = ord(resp[0])
        self.log.info("Telescope model is a %s" % NexStar.models[i])
        return NexStar.models[i]

    def echo(self, s):
        """
        echo function to test communication
        """
        self.ser.write("K" + s[0])
        resp = self.ser.read(2)
        self.log.info("Sending echo command to mount:  %s -> %s" %
                      (s[0], resp[0]))
        return resp[0]

    def aligned(self):
        """
        check if alignment is complete
        """
        self.ser.write("J")
        resp = self.ser.read(2)
        align = ord(resp[0])
        if align == 1:
            self.log.info("Mount is aligned.")
            return True
        else:
            self.log.info("Mount is not aligned.")
            return False

    def goto_in_progress(self):
        """
        check if there is a GOTO in progress
        """
        self.ser.write("L")
        resp = self.ser.read(2)
        self.log.info("Is the Mount in the middle of a GOTO?")
        if resp[0] == "0":
            self.log.info("\t No.")
            return False
        else:
            self.log.info("\t Yes.")
            return True

    def cancel_goto(self):
        """
        cancel a GOTO command
        """
        self.ser.write("M")
        resp = self.ser.read(1)
        if resp == '#':
            self.log.info("Mount GOTO command cancelled.")
            return True
        else:
            self.log.error("Error cancelling GOTO command.")
            return False

    def site(self):
        """
        use mount information to create an ephem.Observer() object for use with
        catalogs and such.
        """
        s = ephem.Observer()
        gps_lock = self.is_gps_linked()
        if gps_lock:
            self.info.log("Setting current site from GPS.")
            s.lat = self.get_gps_latitude()
            s.long = self.get_gps_longitude()
            s.date = self.get_gps_time()
        else:
            self.info.log("Setting current site from handset and computer.")
            s.lat, s.long = self.get_location()
            s.date = ephem.now()
        s.elevation = 3200
        s.temp = 10
        s.compute_pressure()
        s.horizon('-6')
        return s

    def nudge(self, direction, rate):
        """
        macro to do a move in a direction for 1 sec and then stop without 
        interrupting tracking. no idea why i need to repeat the commands to get 
        it to work.  got information from:  NexStar_AUX_Commands_10.pdf
        """
        if rate not in range(10):
            self.log.error("Must specify move rate in valid range of 0-9")
            return False
        if direction not in self.fixed_slew.keys():
            self.log.error("Must specify valid direction: Up, Down, Left, or Right.")
            return False
        destid = self.fixed_slew[direction][0]
        msgid = self.fixed_slew[direction][1]
        cmd = struct.pack("BBBBBB", 0x50, 2, destid, msgid, rate, 1)
        self.ser.write(cmd)
        self.ser.write(cmd)
        time.sleep(1)
        cmd = struct.pack("BBBBBB", 0x50, 2, destid, msgid, 0, 1)
        self.ser.write(cmd)
        self.ser.write(cmd)
        resp = self.ser.read(6)
        self.set_tracking_mode(1)
        return resp

