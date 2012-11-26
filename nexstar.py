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

import serial
import io
import sys
import ephem
import struct


class NexStar:
    """
    main class to encapsulate NexStar interface and operation
    """
    
    tracking_modes = ["Off", "Alt/Az", "EQ North", "EQ South"]
    
    def __init__(self, port="/dev/tty.usbserial"):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 9600
        self.ser.timeout = 3.5
        self.ser.open()

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
        rev = a.norm/(2.0 * ephem.pi)
        if precise:
            return "%8x" % int(rev * 4294967296)
        else:
            return "%4x" % int(rev * 65536)

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
            print "Slewing to RA=%s, Dec=%s...." % (ra, dec)
            return True
        else:
            print "Error in slew command..."
            resp = self.ser.read(1)
            return False

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
            print "Slewing to Az=%s, El=%s...." % (az, el)
            return True
        else:
            print "Error in slew command..."
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
            print "Syncing mount to RA=%s, Dec=%s...." % (ra, dec)
            return True
        else:
            print "Error in sync command..."
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
            print "Current tracking mode is: %s" % NexStar.tracking_modes[mode]
            return mode
        else:
            print "Error querying tracking mode."
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
            print "Successfully set tracking mode to: %s" % \
                    NexStar.tracking_modes[mode]
            return True
        else:
            print "Error setting tracking mode."
            return False
            
    def set_slew_rate(self, rate, fixed=True):
        """
        set the mount's slew rate.  fixed takes a range of 0-9 with 0 being
        stop. the values mimic the hand control rates. otherwise the rate 
        is given in arcseconds/second. 
        """
        if fixed:
            assert rate in range(10), \
            "Fixed slew rates must be integers in range 0-9."
            for i in [36, 37]:
                for j in [16, 17]:
                    cmd = "P" + chr(2) + chr(j) + chr(i) \
                              + chr(rate) + chr(0) + chr(0) + chr(0)
                    self.ser.write(cmd)
                    resp = self.ser.read(1)
                    if resp != '#':
                        print "Error setting slew rates."
                        return False
        else:
            assert rate >= 0, 'Slew rate must be >= 0!'
            rateHigh = (int(rate) * 4) / 256
            rateLow = (int(rate) * 4) % 256
            for i in [6, 7]:
                for j in [16, 17]:
                    cmd = "P" + chr(3) + chr(j) + chr(i) \
                              + chr(rateHigh) + chr(rateLow) + chr(0) + chr(0)
                    self.ser.write(cmd)
                    resp = self.ser.read(1)
                    if resp != '#':
                        print "Error setting slew rates."
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
        return time
        
    