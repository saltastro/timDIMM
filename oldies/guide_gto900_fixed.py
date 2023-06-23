#!/usr/bin/env python
import os
import time
import numpy as np
from pygto900 import GTO900


#set up the telescope

def guide_gto900(tol=100): 
   """Script for guiding the GTO900 based on the output from measure_seeing"""

   """Laure (11-04-2015): Inverted 'Move East' and 'Move West' commands as
   it was pushing the spots off the FOV instead of re-centering them."""

   """Marissa (16-12-2016): Corrected 'Move East' and 'Move West' commands and fixed the test for if side=="w" to if side=="west"
   That was actually why it moved stars off CCD for 50% of the scenarios. It always executed the 'else'"""
 
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
       if side == 'west':
#           print "Move East."
#           g.move('e')
           print "I am west of the pier and too low on the CCD"
           print "Move West."
           g.move('w')
       else:
#           print "Move West."
#           g.move('w')
           print "I am east of the pier and too low on the CCD"
           print "Move East."
           g.move('e')
   if maxy > 240-tol:
       if side == 'west':
#           print "Move West."
#           g.move('w')
           print "I am west of the pier and too high on the CCD"
           print "Move East."
           g.move('e')
       else:
#           print "Move East."
#           g.move('e')
           print "I am east of the pier and too high on the CCD"
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
