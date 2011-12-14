#!/usr/bin/env python

import serial
import io 
import sys
from binutils import *

class OxWagon:
   '''Class variables'''
   pwr_delay = "0300"
   watch_delay = "0900"
   state = {}
   
   commands = { 'RESET':  "2C008000",
                'OPEN':   "10428C00",
                'CLOSE':  "10218000",
              }

   reg_106e_map = ['Manual Close Drop Roof', 
                   'Manual Open Drop Roof', 
                   'Manual Close Slide Roof', 
                   'Manual Open Slide Roof', 
                   'Forced Rain Closure', 
                   'Raining', 
                   False,
                   'Drop Roof Slowdown', 
                   'Drop Roof Moving', 
                   'Drop Roof Opened', 
                   'Drop Roof Closed',
                   'Remote Enabled', 
                   'Slide Roof Slowdown', 
                   'Slide Roof Moving',
                   'Slide Roof Opened', 
                   'Slide Roof Closed']

   reg_106f_map = ['Watchdog Tripped', 
                   False, 
                   False, 
                   False, 
                   False, 
                   False,
                   'Closed due to Power Failure', 
                   False, 
                   False,
                   'Emergency Stop', 
                   'Power Failure',
                   'Proximity Close Drop Roof', 
                   'Proximity Open Drop Roof', 
                   'Proximity Close Slide Roof', 
                   'Proximity Open Slide Roof',
                   'Lights On']

   def __init__(self, port="/dev/tty.PL2303-00002006"):
      self.ser = serial.Serial(port, bytesize=7, parity=serial.PARITY_EVEN, timeout=1)
      self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser), newline='\r\n')
      self.status()

   def command(self, cmd):
      cmd_header = ":01101064000408"
      cmd = cmd_header + cmd + self.watch_delay + self.pwr_delay

      sum = checksum(cmd + "0000")
      to_send = "%s%x\n" % (cmd, sum)
      to_send = to_send.upper()

      self.sio.write(unicode(to_send))
      self.sio.flush()

      resp = self.sio.readline()
      return resp

   def open(self):
      self.command(self.commands['OPEN'])

   def close(self):
      self.command(self.commands['CLOSE'])

   def reset(self):
      self.command(self.commands['RESET'])

   def status(self):
      self.sio.write(unicode(":0103106E000579\n"))
      self.sio.flush()

      resp = self.sio.readline()

      reg_106e = hex2bin(resp[7:11])
      reg_106f = hex2bin(resp[11:15])

      for i in range(16):
         if self.reg_106e_map[i]:
            if reg_106e[i] == '1':
               self.state[self.reg_106e_map[i]] = True
            else:
               self.state[self.reg_106e_map[i]] = False

      for i in range(16):
         if self.reg_106f_map[i]:
            if reg_106f[i] == '1':
               self.state[self.reg_106f_map[i]] = True
            else:
               self.state[self.reg_106f_map[i]] = False

      return self.state

if __name__=='__main__':
   o = OxWagon()
   if len(sys.argv) == 1:
      print "Usage: ox_wagon.py <OPEN|CLOSE|RESET|STATUS>"
   else:
      if sys.argv[1].lower() == 'status':
         state = o.status()
         for k,v in state.items():
            print "%30s : \t %s" % (k,v)
      else:
         eval("o.%s()" % sys.argv[1].lower())
