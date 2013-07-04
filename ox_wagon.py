#!/usr/bin/env python

"""
the OxWagon class implements the most important features required to control
the ox wagon enclosure.
"""

import serial
import io
import sys
from binutils import *


class OxWagon:
    # set a 2 minute power outage delay
    pwr_delay = "0120"
    # set a 5 minute watchdog timer delay
    watch_delay = "0300"

    # cache the state when status() is queried
    state = {}

    # dict of most commonly used commands
    commands = {'RESET':    "2C008000",
                'OPEN':     "10428C02",
                'CLOSE':    "14218000",
                'MONITOR':  "14228C02",
                'SCOPE':    "00000002",
                'LIGHT':    "00000001",
                'OFF':      "00000000",
                }

    # bit map for the first 16-bit register used to monitor status
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

    # bit map for the second register
    reg_106f_map = ['Watchdog Tripped',
                    False,
                    False,
                    False,
                    False,
                    'Telescope Powered On',
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

    def __init__(self, port="/dev/tty.usbserial-A700dz6N"):
        '''
        we use the py27-serial package to implement RS232 communication.
        beware, the port may change if the USB-RS232 cable is ever moved
        to a different port
        '''
        self.ser = serial.Serial(port,
                                 bytesize=7,
                                 parity=serial.PARITY_EVEN,
                                 timeout=1)
        # use this trick to make sure the CR-LF conversions are
        # handled correctly
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser,
                                                      self.ser),
                                    newline='\r\n')
        self.sio.flush()
        self.status()

    def command(self, cmd):
        '''
        take a hexadecimal string, build a command out of it by tacking
        on the delay parameters, and calculating the checksum.
        '''
        cmd_header = ":01101064000408"
        cmd = cmd_header + cmd + self.watch_delay + self.pwr_delay

        # use checksum from binutils.py
        sum = checksum(cmd + "0000")
        to_send = "%s%x\n" % (cmd, sum)
        to_send = to_send.upper()

        self.sio.write(unicode(to_send))
        self.sio.flush()

        resp = self.sio.readline()
        return resp

    def open(self):
        '''
        use pre-defined command to open the ox wagon completely
        '''
        self.command(self.commands['OPEN'])

    def monitor(self):
        '''
        use pre-defined command to open the ox wagon slide roof only
        '''
        self.command(self.commands['MONITOR'])

    def close(self):
        '''
        use pre-defined command to close the ox wagon
        '''
        self.command(self.commands['CLOSE'])

    def reset(self):
        '''
        use pre-defined command to reset the ox wagon controller and
        clear forced closure bits
        '''
        self.command(self.commands['RESET'])

    def status(self):
        '''
        send pre-defined command to query status and parse response into
        dict that is cached into state{} and also returned to caller.
        '''
        self.sio.write(unicode(":0103106E000579\n"))
        self.sio.flush()

        resp = self.sio.readline()

        # use hex2bin from binutils.py
        reg_106e = hex2bin(resp[7:11])
        reg_106f = hex2bin(resp[11:15])

        # use bit maps and parse into dict of boolean values
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

# handle running this as a standalone script.
if __name__ == '__main__':
    o = OxWagon()
    if len(sys.argv) == 1:
        print "Usage: ox_wagon.py <OPEN|CLOSE|RESET|STATUS>"
    else:
        if sys.argv[1].lower() == 'status':
            state = o.status()
            for k, v in state.items():
                print "%30s : \t %s" % (k, v)
        else:
            # eval is your friend!
            eval("o.%s()" % sys.argv[1].lower())
