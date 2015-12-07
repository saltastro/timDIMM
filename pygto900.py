#!/usr/bin/env python
"""pygto900 contains commands to interface with a astro-physics gto900 mount
"""

import serial
import io
import sys
import string
import math
import time
from binutils import *
from datetime import datetime

from astropy.coordinates import Angle


def airmass(a):
    ang = Angle(90, unit='degree') - a
    return 1.0/math.cos(ang.radian)

class GTO900:
   def __init__(self, port="/dev/ttyUSBtoGTO900"):
        '''
        we use the py27-serial package to implement 
        communication.to the telescope.  The port may change
        '''
        self.ser = serial.Serial(port,
                                 baudrate=9600,
                                 bytesize=8,
                                 timeout=3)
 
        self.catalog={}

   def __enter__(self):
       self.clear()
       self.long_format()
       self.set_current_date()
       self.set_local_time()
       return self
  
   def __exit__(self, errtype, value, traceback):
       self.close()
       if errtype is not None:
           raise 

   def command(self, command):
        self.ser.write(command)

   def read(self):
        resp = self.ser.readline()
        return resp.strip('#')

   def close(self):
        self.clear()
        self.ser.close()

   #check the result
   def check(self):
        result = self.ser.read(1)
        self.clear()
        return result

   #clear all the values
   def clear(self):
        self.command('#')

   #set the format as long
   def long_format(self):
        self.command("#:U#")

   # set the offset from greenwich mean time
   def set_gmt_offset(self, hrs):
        self.command("#:SG %s#" % hrs)
        return self.check()

   # set the current longitude
   def set_longitude(self, d, m, s):
       long_str = "%d*%02d:%02d" % (d, m, s)
       self.command("#:Sg %s#" % long_str )
       return self.check()

   # set the current latitude
   def set_latitude(self, d, m, s):
       lat_str = "%d*%02d:%02d" % (d, m, s)
       self.command("#:St %s#" % lat_str)
       return self.check()

   # set current date (MM/DD/YY)
   def set_current_date(self):
       ut = datetime.utcnow()
       date_str = ut.strftime("%m/%d/%Y")
       self.command("#:SC %s#" % date_str)
       blah = self.read()
       return self.read()

   # set local time (HH:MM:SS)
   def set_local_time(self):
       sast = datetime.now()
       time_str = sast.strftime("%H:%M:%S")
       self.command("#:SL %s#" % time_str)
       return self.check()
  

   # get UTC offset from GTO900
   def get_UTC_offset(self):
       self.command("#:GG#")
       output = self.read()
       #sign, h, m, s, ds = string.scan(/(.)(\d+):(\d+):(\d+).(\d+)/)[0]
       return output

   # get current site longitude
   def get_longitude(self):
       self.command("#:Gg#")
       output = self.read()
    #  sign, d, m, s = string.scan(/(.)(\d+)\*(\d+):(\d+)/)[0]
    # output = sign + d + ":" + m + ":" + s
       return output.replace('*', ':')

   # get current site latitude
   def get_latitude(self):
       self.command("#:Gt#")
       output = self.read()
       return output.replace('*', ':')

   # get local time
   def get_local_time(self):
       self.command("#:GL#")
       output = self.read()
       return output 

   # get local date
   def get_local_date(self):
       self.command("#:GC#")
       output = self.read()
       output = output.replace(':', '/')
       return output

   # get LST
   def lst(self):
       self.command("#:GS#")
       return self.read()

   #get RA
   def ra(self):
       self.command("#:GR#")
       return self.read()

   #get dec
   def dec(self):
       self.command("#:GD#")
       d = self.read()
       d = d.replace('*', ':')
       return d

   # read the current altitude from the GTO900
   def alt(self):
       self.command("#:GA#")
       output = self.read()
       return output.replace('*', ':')
 
   # calculate current GTO900 airmass
   def airmass(self):
    a = Angle(self.alt(), unit='degree')
    return airmass(a)

   # read the current azimuth from the GTO900
   def az(self):
       self.command("#:GZ#")
       output = self.read()
       if output:
           return output.replace('*',':')
       else:
           return None

   # command the GTO900 to slew to the target RA and Dec
   def slew(self):
       self.command("#:MS#")
       result=self.read()
       if result: 
           print 'Slewing...'
       else:
           print result

   # command the GTO900 to move in the given direction at 
   # the current guide or centering rate
   def move(self, mdir):
       if mdir in ["e","n","s","w"]:
           self.command("#:M%s#" % mdir)

   # command the GTO900 to move in the given direction at 
   # the current guide or centering rate 
   # for a given number of ms
   def move_ms(self,mdir, ms):
       if mdir in ["e","n","s","w"]:
           self.command("#:M%s%s#" % (mdir, ms))

   # swap north-south buttons
   def swap_ns(self):
       self.command("#:NS#")

   # swap east-west buttons
   def swap_ew(self):
       self.command("#:EW#")

   # command the GTO900 to stop motion in the given direction
   def halt(self, mdir):
       if mdir in ["e","n","s","w"]:
           self.command("#:Q%s#" % mdir)

   # command the GTO900 to halt all mount motion
   def haltall(self):
       self.command("#:Q#")

   # select guide rate
   def select_guide_rate(self, rate=''):
       if rate in ['', '0', '1', '2']:
           self.command("#:RG%s#" % rate)

   # select centering rate
   def select_center_rate(self, rate=''):
       if rate in ['', '0', '1', '2']: 
           self.command("#:RC%s#" % rate)

   # set centering rate
   def set_center_rate(self, rate):
      if rate > 0 and rate < 256:
         self.command("#:Rc%s#" % rate)

   # select slew rate
   def select_slew_rate(self, rate=''):
       if rate in ['', '0', '1', '2']: 
           self.command("#:RS%s#" % rate)

   # set slew rate
   def set_slew_rate(self, rate):
       if rate > 0 and rate <= 1200:
           self.command("#:Rs %s#" % rate)

   # select tracking rate
   def select_tracking_rate(self, rate=''):
       if rate in ['', '0', '1', '2', '9']: 
           self.command("#:RS%s#" % rate)

   # set RA tracking rate
   def set_RA_rate(self, rate):
       self.command("#:RR %s#" % rate)

   # set Dec tracking rate
   def set_Dec_rate(self,rate):
       self.command("#:RD %s#" % rate)

   # set amount of Dec backlash compensation (in seconds)
   def set_Dec_backlash(self,sec):
       self.command("#:Bd 00*00:%s#" % sec)
       return self.read()

   # set amount of RA backlash compensation (in seconds)
   def set_RA_backlash(self, sec):
       self.command("#:Br 00:00:%s#" %sec)
       return self.read()

   # invoke parked mode
   def park_mode(self):
       self.command("#:KA#")

   # invoke parked mode
   def park_mode_test(self):
       self.command("#:RG2#")
       self.command("#:Me#")

   # park off
   def park_off(self):
       self.command("#PO:#")
  
   # query pier
   def pier(self):
       self.command("#:pS#")
       return self.read()

   # sync mount
   def sync(self):
       self.command("#:CM#")
       return self.read()

   # re-cal mount
   def recal(self):
       self.command("#:CMR#")
       return self.read() 

   # define commanded RA
   def command_ra(self, h, m, s):
       r_str = "%02d:%02d:%02d" % (h,m,s)
       self.command("#:Sr %s#" % r_str)
       return self.check() 

   def command_ra_raw(self, r):
       self.command("#:Sr %s#" % r)
       return self.check() 

   # define commanded Dec
   def command_dec(self, d, m, s):
       d_str = "%d*%02d:%02d" % (d,m,s)
       self.command("#:Sd %s#" % d_str)
       return self.check() 

   def command_dec_raw(self, d):
      self.command("#:Sd %s#" % d)
      return self.check()

   # define commanded Alt
   def command_alt(self, d, m, s):
       alt_str = "+%d*%02d:%02d" % (d,m,s)
       self.command("#:Sa %s#" % alt_str)
       return self.check() 

   # define commanded Az
   def command_az(self, d, m, s):
       az_str = "%d*%02d:%02d" % (d,m,s)
       self.command("#:Sz %s#" % az_str)
       return self.check()

   # increase reticle brightness
   def increase_reticle_brightness(self):
       self.command("#:B+#")

   # decrease reticle brightness
   def decrease_reticle_brightness(self):
       self.command("#:B-#")

   # command the focuser to move inward (toward the primary)
   def focus_in(self):
       self.command("#:F+#")

   # command the focuser to move outward (away from the primary)
   def focus_out(self):
       self.command("#:F-#")

   # focus fast
   def focus_fast(self):
       self.command("#:FF#")

   # focus slow
   def focus_slow(self):
       self.command("#FS#")

   # halt all focuser motion
   def focus_halt(self):
       self.command("#:FQ#")

   # get telescope firmware
   def get_firmware(self):
       self.command("#:V#")
       return self.read()

   # startup procedure
   def startup(self):
       self.clear()
       self.clear()
       self.clear()
       self.long_format()



def status(g):
    """Chck the values for the telescope"""
    ra = g.ra()
    dec = g.dec()
    lst = g.lst()
    ha = Angle('%s hour' % lst) - Angle('%s hour' % ra)
    alt = g.alt()
    az = g.az()
    a = Angle(alt, unit='degree')
    z = airmass(a)
    p = g.pier()
    return ra,dec,ha,lst,alt,az,z,p

def park_position(g):
    '''
    Move the telescope to point directly South.
    '''
    print 'sending the telescope to the park position...'
    g.command_alt(32, 22, 33)
    g.command_az(180,00,00)  
    g.slew()
    g.park_mode()


def slew(g, ra, dec, niter=100):
    """Slew to a location

    Paramters
    ---------

    ra: astropy.coordinates.Angle
       Right Ascension of source

    dec: astropy.coordinates.Angle
       Declination of source

    niter: int
       Number of loops to attempt if monitoring progress
    """
    g.command_ra(ra.hms[0], ra.hms[1], ra.hms[2])
    g.command_dec(dec.dms[0], dec.dms[1], dec.dms[2])
    g.slew()

    for i in range(niter):
        try:
          r = Angle(g.ra(), unit='hour')
          d = Angle(g.dec(), unit='degree')
        except Exception,e:
            print e
            continue
        dist = ((r.degree - ra.degree)**2 + (d.degree-dec.degree)**2)**0.5
        if dist < 1.0/60.0:
           print 'Done Slewing'
           return 
        else:
           print '%5.2f degrees to go until target' % dist
    return


def init(g):
    """Initialize the telescope"""
    print "Initializing mount...."
    g.startup()
    return

def nudge(g, mdir):
    """Nudge the telescope in one direction"""
    g.set_center_rate(10)
    g.move(mdir)
    time.sleep(1)
    g.halt(mdir)
    time.sleep(1)

def usage():
   """Print the usage string"""

   usage_str = """
Usage for pygto900:

python pygto900 [init/status/log/move/nudge/slew/sync/park/help] [optional]

"""
   print usage_str


if __name__=='__main__':
   task = sys.argv[1].lower()
 
   if len(sys.argv) < 2: 
      usage()
      exit()

   if task in ['help']: 
      usage()
      exit()
 
   with GTO900() as g:
       if task == 'status':
           results = status(g)
           output ="At RA = %s, Dec = %s, HA = %s, LST = %s, Alt = %s, Az = %s, secz = %.2f, on the %s side of the pier" % results
           print  output 
       elif task == 'log':
           results = status(g)
           print '%s %s %s %s %s %s %.2f %s' % results
       elif task == 'init':
           init(g)
       elif task == 'park':
           g.park_mode()
       elif task == 'park_position':
           park_position(g)
       elif task == 'park_off':
           g.park_off()
       elif task == 'sync':
           g.sync()
       elif task == 'move':
           g.move(sys.argv[2])
       elif task == 'nudge':
           nudge(g, sys.argv[2])
       elif task == 'slew':
           ra = Angle(sys.argv[2], unit='hour')
           dec = Angle(sys.argv[3], unit='degree')
           slew(g, ra, dec)
       elif task == 'help':
           usage()
       else:
           usage()

#y=GTO900()
#print y.ra(), y.dec() 
#y.lst(), y.get_local_time(), y.get_local_date()
#print y.get_UTC_offset(), y.get_longitude(), y.get_latitude()
#print y.command_ra(12,01,34)
#print y.command_dec(-37,01,34)
#print y.slew()
#print y.ra(), y.dec()
#print y.alt(), y.az()
#print y.move('e')
#print y.alt(), y.az()

