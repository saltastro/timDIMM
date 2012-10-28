import serial
from time import sleep

port=serial.Serial("/dev/ttyS0",
                   9600,
                   parity = "N",
                   bytesize = 8,
                   stopbits = 1,
                   rtscts = 0,
                   xonxoff = 0,
                   timeout = 1)

port.write('c')        # Get dome status
print port.readline()

sleep(1.)

port.write('a')        # Open dome
#port.write('b')        # Close dome

while 1:
    port.write('c')
    print port.readline()
    sleep(1.)
