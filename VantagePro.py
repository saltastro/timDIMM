#!/usr/bin/env python

import sys
import serial
import struct
import logger
import logging
import ctypes
import time
import sqlite3 as sql
from threading import Thread


def f2c(f):
    return (f - 32.0)*5.0/9.0

def in2mm(inches):
    return 25.4 * inches

def miles2km(miles):
    return 1.60934 * miles
             
def inHg2mb(inHg):
    return 33.8638866667 * inHg


class VantagePro:

    def __init__(self, port="/dev/tty.usbserial-A90160BN", baudrate=19200, timeout=1.5):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.log = logger.ColorLog(logging.getLogger(__name__))
        self.log.addHandler(logger.fh)
        self.ack = struct.pack("B", 0x06)
        self.data = {}
        self.bar_trends = { -60: "Falling Rapidly",
                            -20: "Falling Slowly",
                              0: "Steady",
                             20: "Rising Slowly",
                             60: "Rising Rapidly"}
        self.units = { 'Barometer Trend': '',
                       'Barometer': 'mm Hg',
                       'Inside Temperature': 'C',
                       'Inside Humidity': '%',
                       'Outside Temperature': 'C',
                       'Wind Speed': 'km/h',
                       'Ave Wind Speed': 'km/h',
                       'Wind Direction': '',
                       'Outside Humidity': '%',
                       'Rain Rate': 'mm/hour',
                       'UV Index': '',
                       'Solar Radiation': 'W/m^2',
                       'Day Rain': 'mm',
                       'Month Rain': 'mm',
                       'Year Rain': 'mm',
                       'Transmitter Battery Status': '',
                       'Console Battery Voltage': 'V' }
        # this table is copied from the VantagePro serial protocol document
        self.crc_table = [0x0,  0x1021,  0x2042,  0x3063,  0x4084,  0x50a5,  0x60c6,  0x70e7,
             0x8108,  0x9129,  0xa14a,  0xb16b,  0xc18c,  0xd1ad,  0xe1ce,  0xf1ef,
             0x1231,  0x210,  0x3273,  0x2252,  0x52b5,  0x4294,  0x72f7,  0x62d6,
             0x9339,  0x8318,  0xb37b,  0xa35a,  0xd3bd,  0xc39c,  0xf3ff,  0xe3de,
             0x2462,  0x3443,  0x420,  0x1401,  0x64e6,  0x74c7,  0x44a4,  0x5485,
             0xa56a,  0xb54b,  0x8528,  0x9509,  0xe5ee,  0xf5cf,  0xc5ac,  0xd58d,
             0x3653,  0x2672,  0x1611,  0x630,  0x76d7,  0x66f6,  0x5695,  0x46b4,
             0xb75b,  0xa77a,  0x9719,  0x8738,  0xf7df,  0xe7fe,  0xd79d,  0xc7bc,
             0x48c4,  0x58e5,  0x6886,  0x78a7,  0x840,  0x1861,  0x2802,  0x3823,
             0xc9cc,  0xd9ed,  0xe98e,  0xf9af,  0x8948,  0x9969,  0xa90a,  0xb92b,
             0x5af5,  0x4ad4,  0x7ab7,  0x6a96,  0x1a71,  0xa50,  0x3a33,  0x2a12,
             0xdbfd,  0xcbdc,  0xfbbf,  0xeb9e,  0x9b79,  0x8b58,  0xbb3b,  0xab1a,
             0x6ca6,  0x7c87,  0x4ce4,  0x5cc5,  0x2c22,  0x3c03,  0xc60,  0x1c41,
             0xedae,  0xfd8f,  0xcdec,  0xddcd,  0xad2a,  0xbd0b,  0x8d68,  0x9d49,
             0x7e97,  0x6eb6,  0x5ed5,  0x4ef4,  0x3e13,  0x2e32,  0x1e51,  0xe70,
             0xff9f,  0xefbe,  0xdfdd,  0xcffc,  0xbf1b,  0xaf3a,  0x9f59,  0x8f78,
             0x9188,  0x81a9,  0xb1ca,  0xa1eb,  0xd10c,  0xc12d,  0xf14e,  0xe16f,
             0x1080,  0xa1,  0x30c2,  0x20e3,  0x5004,  0x4025,  0x7046,  0x6067,
             0x83b9,  0x9398,  0xa3fb,  0xb3da,  0xc33d,  0xd31c,  0xe37f,  0xf35e,
             0x2b1,  0x1290,  0x22f3,  0x32d2,  0x4235,  0x5214,  0x6277,  0x7256,
             0xb5ea,  0xa5cb,  0x95a8,  0x8589,  0xf56e,  0xe54f,  0xd52c,  0xc50d,
             0x34e2,  0x24c3,  0x14a0,  0x481,  0x7466,  0x6447,  0x5424,  0x4405,
             0xa7db,  0xb7fa,  0x8799,  0x97b8,  0xe75f,  0xf77e,  0xc71d,  0xd73c,
             0x26d3,  0x36f2,  0x691,  0x16b0,  0x6657,  0x7676,  0x4615,  0x5634,
             0xd94c,  0xc96d,  0xf90e,  0xe92f,  0x99c8,  0x89e9,  0xb98a,  0xa9ab,
             0x5844,  0x4865,  0x7806,  0x6827,  0x18c0,  0x8e1,  0x3882,  0x28a3,
             0xcb7d,  0xdb5c,  0xeb3f,  0xfb1e,  0x8bf9,  0x9bd8,  0xabbb,  0xbb9a,
             0x4a75,  0x5a54,  0x6a37,  0x7a16,  0xaf1,  0x1ad0,  0x2ab3,  0x3a92,
             0xfd2e,  0xed0f,  0xdd6c,  0xcd4d,  0xbdaa,  0xad8b,  0x9de8,  0x8dc9,
             0x7c26,  0x6c07,  0x5c64,  0x4c45,  0x3ca2,  0x2c83,  0x1ce0,  0xcc1,
             0xef1f,  0xff3e,  0xcf5d,  0xdf7c,  0xaf9b,  0xbfba,  0x8fd9,  0x9ff8,
             0x6e17,  0x7e36,  0x4e55,  0x5e74,  0x2e93,  0x3eb2,  0xed1,  0x1ef0]
        self.ser.open()
        self.log.info("Weather station opened on port %s at baudrate %d." % (port, baudrate))
        self.firmware()
        self.settime()

    def checksum(self, data, start=0):
        # need to use ctypes here to enforce the uint16 length. otherwise the << 8
        # shift will cause an automatic recast to uint32.
        crc = ctypes.c_uint16(start)
        # if we specify a starting point, we're checking a CRC we've received.
        # it will come as an int and we need to repack it into a string.
        if start > 0:
            # pack the input in big endian order
            data = struct.pack(">H", data)
        for b in data:
            index = (crc.value >> 8) ^ ord(b)
            # need to make the shift in place so that it stays in C.  otherwise python will
            # recast to uint32 which is bad.
            crc.value <<= 8
            crc.value = self.crc_table[index] ^ crc.value
        return crc.value

    def flush(self):
        self.log.info("Clearing serial connection to weather station....")
        while self.ser.read(1):
            self.log.info("\t-> Flushing...")
        self.log.info("\t-> Done!")
        
    def wake(self):
        self.log.info("Waking weather station...")
        self.ser.write("\n")
        resp = self.ser.read(2)
        if resp != "\n\r":
            self.log.warn("Wake attempt failed.  Retrying...")
            self.ser.write("\n")
            resp = self.ser.read(2)
            if resp != "\n\r":
                self.log.warn("Wake attempt failed again.  Giving up...")
                return False
            else:
                self.log.info("Weather station awake.")
                return True
        else:
            self.log.info("Weather station awake.")

    def test(self):
        self.log.info("Sending test string to weather station....")
        self.ser.write("TEST\n")
        resp = self.ser.read(8)
        if resp == "\n\rTEST\n\r":
            self.log.info("Weather station test successful.")
            return True
        else:
            self.log.error("Weather station test unsuccessful: %s" % resp)
            return False

    def rxcheck(self):
        self.log.info("Sending RXCHECK command to weather station...")
        self.ser.write("RXCHECK\n")
        resp = self.ser.readline()
        flag = self.ser.readline().strip()
        self.log.info("\t-> Weather station status: %s" % flag)
        data = self.ser.readline().strip()
        self.ser.read(1)
        self.log.info("\t-> Weather station diagnostics: %s" % data)
        return data

    def firmware(self):
        self.log.info("Querying weather station firmware:")
        self.ser.write("VER\n")
        resp = self.ser.readline()
        resp = self.ser.readline()
        datecode = self.ser.readline().strip()
        self.ser.write("NVER\n")
        resp = self.ser.readline()
        resp = self.ser.readline()
        firmware = self.ser.readline().strip()
        self.ser.read(1)
        self.log.info("\t-> Version %s (%s)" % (firmware, datecode))
        return (firmware, datecode)

    def gettime(self):
        self.log.info("Querying time from weather station.")
        self.ser.write("GETTIME\n")
        ack = self.ser.read(1)
        if ack != self.ack:
            self.log.error("Error reading time from weather station.")
            self.ser.read(20)
        resp = self.ser.read(6)
        (s, m, h, d, mo, yr) = struct.unpack("BBBBBB", resp)
        yr += 1900
        crc = struct.unpack(">H", self.ser.read(2))[0]
        check = self.checksum(crc, start=crc)
        if check == 0:
            self.log.info("\t-> query successful.")
            time = "%d-%02d-%02d %02d:%02d:%02d" % (yr, d, mo, h, m, s)
            self.log.info("\t-> reported time is %s" % time)
            return time
        else:
            self.warn("CRC error reading time from weather station.")
            return False
        
    def settime(self):
        t = time.localtime()
        self.log.info("Setting time on weather station to %s" %
                      time.strftime("%Y-%d-%m %H:%M:%S"))
        to_send = struct.pack("BBBBBB", t.tm_sec, t.tm_min, t.tm_hour,
                              t.tm_mday, t.tm_mon, t.tm_year-1900)
        crc = self.checksum(to_send)
        to_send += struct.pack(">H", crc)
        self.ser.write("SETTIME\n")
        ack = self.ser.read(1)
        if ack != self.ack:
            self.log.error("\t-> SETTIME command not accepted.")
            return False
        self.ser.write(to_send)
        ack = self.ser.read(1)
        if ack != self.ack:
            self.log.error("\t-> Could not set the time!")
            self.flush()
            return False
        else:
            self.log.info("\t-> time successfully set.")
            return True

    def set_archive_interval(self, interval):
        if interval not in [1, 5, 10, 15, 30, 60, 120]:
            self.log.warn("Specify valid logging interval (1, 5, 10, 15, 30, 60, or 120 min)")
            return False
        else:
            self.ser.write("SETPER %d\n" % interval)
            time.sleep(5)
            ack = self.ser.read(1)
            if ack != self.ack:
                self.log.error("Error setting logging interval!")
                self.flush()
                return False
            else:
                self.log.info("Logging interval set to %d min." % interval)
                return True

    def lamp(self, state=False):
        if state:
            self.log.info("Turning weather station console light on.")
            self.ser.write("LAMPS 1\n")
        else:
            self.log.info("Turning weather station console light off.")
            self.ser.write("LAMPS 0\n")
        self.ser.readline()
        ack = self.ser.readline().strip()
        self.ser.read(1)
        if ack != "OK":
            self.log.error("Error setting weather station console light!")
            self.flush()
            return False
        else:
            return True

    def get_data(self):
        self.log.info("Querying data from weather station.")
        self.ser.write("LOOP 1\n")
        ack = self.ser.read(1)
        if ack != self.ack:
            self.log.error("Error querying data from weather station!")
            self.flush()
            return False
        packet = self.ser.read(99)
        crc = struct.unpack(">H", packet[97:99])[0]
        check = self.checksum(crc, start=crc)
        if check == 0:
            newdata = {}
            newdata['Barometer Trend'] = self.bar_trends[struct.unpack("b", packet[3])[0]]
            newdata['Barometer'] = in2mm(struct.unpack("H", packet[7:9])[0] / 1000.0)
            newdata['Inside Temperature'] = f2c(struct.unpack("H", packet[9:11])[0] / 10.0)
            newdata['Inside Humidity'] = struct.unpack("B", packet[11])[0]
            newdata['Outside Temperature'] = f2c(struct.unpack("H", packet[12:14])[0] / 10.0)
            newdata['Wind Speed'] = miles2km(struct.unpack("B", packet[14])[0])
            newdata['Ave Wind Speed'] = miles2km(struct.unpack("B", packet[15])[0])
            newdata['Wind Direction'] = struct.unpack("H", packet[16:18])[0]
            newdata['Outside Humidity'] = struct.unpack("B", packet[33])[0]
            newdata['Rain Rate'] = struct.unpack("H", packet[41:43])[0] * 0.2
            newdata['UV Index'] = struct.unpack("B", packet[43])[0]
            newdata['Solar Radiation'] = struct.unpack("H", packet[44:46])[0]
            newdata['Day Rain'] = struct.unpack("H", packet[50:52])[0] * 0.2
            newdata['Month Rain'] = struct.unpack("H", packet[52:54])[0] * 0.2
            newdata['Year Rain'] = struct.unpack("H", packet[54:56])[0] * 0.2
            newdata['Transmitter Battery Status'] = struct.unpack("B", packet[86])[0]
            data = struct.unpack("H", packet[87:89])[0]
            newdata['Console Battery Voltage'] = ((data * 300.0) / 512.0) / 100.0
            return newdata
        else:
            self.log.error("CRC error when querying data from weather station!")
            return False

if __name__ == '__main__':
    v = VantagePro()
    v.flush()
    if len(sys.argv) < 2:
        data = v.get_data()
        for k, val in data.items():
            if type(val) is str:
                print "%27s : %16s" % (k, val)
            elif type(val) is int:
                print "%27s : %16d %s" % (k, val, v.units[k])
            elif type(val) is float:
                print "%27s : %16.2f %s" % (k, val, v.units[k])
            else:
                print "Bad Type: %s" % k
    else:
        cmd = " ".join(sys.argv[1:])
        v.log.info("Sending raw command to weather station: %s" % cmd)
        v.ser.write(cmd + "\n")
        resp = v.ser.read(8192)
        v.log.info("Received response: %s" % resp)
        print resp
