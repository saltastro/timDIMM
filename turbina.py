#!/usr/bin/env python

import socket
import sys

class Turbina:

    status = "OFFLINE"

    def __init__(self, host="massdimm.suth", port=16007):
        try:
            self.sockopen(host, port)
            self.host = host
            self.port = port
            self.status()
        except:
            self.status = "OFFLINE"
            self.sock = None
            
    def sockopen():
        self.sock = socket.create_connection((self.host, self.port))

    def close():
        self.sock.shutdown()
        self.sock.close()
        self.status = "OFFLINE"
        
    
