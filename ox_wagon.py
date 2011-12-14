#!/usr/bin/env python

import serial
import io 
import sys

<<<<<<< HEAD
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

   def __init__(self, port):
      self.ser = serial.Serial(port, bytesize=7, parity=serial.PARITY_EVEN, timeout=1)
      self.sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
      status()
      
   def hex2bin(str):
      bin = ['0000','0001','0010','0011',
             '0100','0101','0110','0111',
             '1000','1001','1010','1011',
             '1100','1101','1110','1111']
      aa = ''
      for i in range(len(str)):
         aa += bin[int(str[i],base=16)]
      return aa

   def checksum(str):
      command = str[1:len(str)-4]
      sum = 0
      for i in range(0, len(command), 2):
         byte = command[i] + command[i+1]
         sum = sum + int(byte, base=16)

      neg = ~sum & 0xFF
      return neg + 1

   def command(cmd):
      cmd_header = ":01101064000408"
      cmd = cmd_header + commands[sys.argv[1]] + watch_delay + pwr_delay

      sum = checksum(cmd + "0000")
      to_send = "%s%x\n" % (cmd, sum)
      to_send = to_send.upper()

      sio.write(unicode(to_send))
      sio.flush()

      resp = sio.readline()
      return resp

   def status():
      self.sio.write(unicode(":0103106E000579\n"))
      self.sio.flush()

      resp = sio.readline()

      reg_106e = hex2bin(resp[7:11])
      reg_106f = hex2bin(resp[11:15])

      for i in range(16):
         if reg_106e_map[i]:
            state[reg_106e[i]] = reg_106e_map[i]

      for i in range(16):
         if reg_106f_map[i]:
            state[reg_106f[i]] = reg_106f_map[i]
=======
def hex2bin(str):
   bin = ['0000','0001','0010','0011',
         '0100','0101','0110','0111',
         '1000','1001','1010','1011',
         '1100','1101','1110','1111']
   aa = ''
   for i in range(len(str)):
      aa += bin[int(str[i],base=16)]
   return aa


def checksum(str):
   command = str[1:len(str)-4]
   sum = 0
   for i in range(0, len(command), 2):
      byte = command[i] + command[i+1]
      sum = sum + int(byte, base=16)

   neg = ~sum & 0xFF

   return neg + 1

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

commands = { 'RESET':  "28008000",
             'OPEN':   "1C428C00",
             'CLOSE':  "14218000",
             'STATUS': "04008000"
           }

commands = { 'RESET':  "2C008000",
             'OPEN':   "10428C00",
             'CLOSE':  "10218000",
             'STATUS': "10008000"
           }

cmd_header = ":01101064000408"
pwr_delay = "0300"
watch_delay = "0900"

ser = serial.Serial('/dev/tty.PL2303-00002006', bytesize=7, parity=serial.PARITY_EVEN, timeout=1)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')

sio.write(unicode(":0103106E000579\n"))
sio.flush()

resp = sio.readline()

if sys.argv[1] == 'STATUS':
   reg_106e = hex2bin(resp[7:11])
   reg_106f = hex2bin(resp[11:15])

   for i in range(16):
      if reg_106e_map[i]:
         print "%s : %s" % (reg_106e[i], reg_106e_map[i])

   for i in range(16):
      if reg_106f_map[i]:
         print "%s : %s" % (reg_106f[i], reg_106f_map[i])

else:
   print "Commanding OX wagon to %s...." % sys.argv[1]

   cmd = cmd_header + commands[sys.argv[1]] + watch_delay + pwr_delay

   sum = checksum(cmd + "0000")
   to_send = "%s%x\n" % (cmd, sum)
   to_send = to_send.upper()

   sio.write(unicode(to_send))
   sio.flush()

   resp = sio.readline()
>>>>>>> 6aebb05d023d578c5efd6a70200530e614d36744


