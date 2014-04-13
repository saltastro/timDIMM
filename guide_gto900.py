#!/usr/bin/env python
import os
import time
import numpy as np
from pygto900 import GTO900


#set up the telescope

def guide_gto900(tol=100): 
   """Script for guiding the GTO900 based on the output from measure_seeing"""
 
   #set up the telescope
   g = GTO900()
   side = g.pier()
   side = side.strip().lower()

   #set up the data
   data = np.loadtxt('init_cen_all')
   
   minx=min(1000.0, data[0,0], data[1,0])
   maxx=max(0.0, data[0,0], data[1,0])
   miny=min(1000.0, data[0,1], data[1,1])
   maxy=max(0.0, data[0,1], data[1,1])
   print side
   print minx, maxx, miny, maxy

   g.set_center_rate(2)
   if maxx > 320-tol:
      print "Move South."
      g.move('s')
   if minx < tol:
      print "Move North."
      g.move('n')
   if miny < tol:
       if side == 'w':
           print "Move West."
           g.move('w')
       else:
           print "Move East."
           g.move('e')
   if maxy > 240-tol:
       if side == 'w':
           print "Move East."
           g.move('e')
       else:
           print "Move West."
           g.move('w')

   time.sleep(1)
   g.haltall()
   time.sleep(1)
   g.clear()
   g.clear()
   g.clear()
   g.close()



if __name__=='__main__':
   guide_gto900()
