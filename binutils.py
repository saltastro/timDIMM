'''misc routines for dealing with binary data'''


def hex2bin(str):
    '''
    take a hexadecimal number as a string and convert it to a binary string
    '''
    bin = ['0000', '0001', '0010', '0011',
           '0100', '0101', '0110', '0111',
           '1000', '1001', '1010', '1011',
           '1100', '1101', '1110', '1111']
    aa = ''
    for i in range(len(str)):
        aa += bin[int(str[i], base=16)]
    return aa


def checksum(str):
    '''twos complement checksum as used by the ox wagon PLC'''
    command = str[1:len(str) - 4]
    sum = 0
    for i in range(0, len(command), 2):
        byte = command[i] + command[i + 1]
        sum = sum + int(byte, base=16)
    neg = ~sum & 0xFF
    return neg + 1
