#!/usr/bin/env python

import os, shutil
import datetime 

import ox_wagon
import pick_star
from find_boxes import find_boxes
from guide_gto900 import guide_gto900
from pygto900 import GTO900, status
from spiral_search_gto900 import spiralsearch
import time
import sys

old_star = None
repeat = 1
niter = 15

spiral_log = '/home/massdimm/spiral.log'

def telescope_info(g):
    '''A method to monitor the telescope position while measuring the seeing
    ---
    If the telescope is in an compromising position, set a flag to stop measure
    seeing and try and point to a different star. This way 
    '''
    warn = False

    alt = g.alt()
    az = g.alt()
    pier = g.pier().strip().lower()
    lst = Angle('%s hour' %g.lst())
    ra = Angle('%s hour' %g.ra())
    dec = Angle('%s degrees' %g.dec()
    ha = lst - ra

    scope = {}
    scope['alt'] = alt
    scope['az'] = az
    scope['pier'] = pier
    scope['lst'] = lst
    scope['ha'] = ha
    scope['ra'] = ra
    scope['dec'] = dec 

    if (pier == 'west') and (ha > Angle('00:45:00.0 degree')):
        warn = True
        print 'WARNING: Telescope could run into the pier'
        print '         Stop measure seeing'

    return warn,scope


while True:
   #kill any existing running camera programs
   os.system('pkill ave_frames')
   os.system('pkill measure_seeing')
   time.sleep(5)

   #Make sure the ox wagon is open
   try:
      ox=ox_wagon.OxWagon()
      ox=ox.open()
   except Exception,e:
      print Exception
      print 'Could not give open command to Ox Wagon'
      pass

   #Warning if telescope is pointing too low
   with GTO900() as g:
        warn, scope = telescope_info(g)  
        if scope['alt'] <= 30.0:
           print '!!!WARNING: Telescope is at an altitude lower than 30 degrees !!!'
           print 'Seeing measurements will not start'
           print 'YOU MAY WANT TO CHECK THE TELESCOPE ALIGNMENT AND POINTING BEFORE STARTING MEASUREMENTS'
           g.park_mode()
           sys.exit()
        else:
           print 'Telescope position checked'

        #pick the star
        try:
           pick_star.pick_star(g)
        except Exception, e:
           print Exception
           print 'Could not pick new star because %s' % e
           print 'WARNING:  YOU MAY WANT TO STOP MEASUREMENT AND START AGAIN'
           g.park_mode()
           exit()

        #check to see if the star is available
        os.system('./ave_frames 10 \!center.fits')
        if not os.path.isfile('center.fits'):
           print Exception
           print 'Center.fits was not created'
           print 'WARNING:  YOU MAY WANT TO STOP MEASUREMENT AND START AGAIN'
           g.park_mode()
           exit()

        nstars = find_boxes('center.fits')
        if nstars < 2:
           nfound, sx, sy = spiralsearch(g,niter=niter)
           sout = open(spiral_log, 'a')
           sout.write('%s %i %i %i\n' % (datetime.datetime.now(), sx, sy, nfound))
           sout.close()
           if nfound == -1:
              print 'Could not find stars in %i iterations' % niter
              g.park_mode()
                
           os.system('./ave_frames 10 \!center.fits')
           nstars = find_boxes('center.fits')


   try:
       current_star=open('current_object').read().strip()
   except:
       old_star = None
       current_star = None

   if (old_star is None) or (old_star != current_star):
      old_star = current_star
  
   #display star and log information
   os.system('cat center.fits | xpaset timDIMM fits')
   os.system('./pygto900.py log >> gto900.log')

   #measure star -- changed this d wn to 1000 from 10000
   os.system("./measure_seeing 10000 `tail -1 gto900.log | cut -d ' ' -f 7` `cat exptime`")

   # adjust the guiding
   guide_gto900()

   #remove file so error caught if it isn't made
   if os.path.isfile('center.fits'): os.remove('center.fits')
 
   #update the documents
   if os.path.isfile('seeing.out'):
       t=datetime.datetime.now()
       centroid_file='centroids_%s.dat' % t.strftime('%Y%m%d-%H%M%S')

       shutil.move('centroids.dat', 'data/%s' % centroid_file)
       os.chdir('data')
       os.system('../dimm_stats.py %s' % centroid_file) 
       os.chdir('../')
       
       os.system('echo "image;text 25 5 # text={Seeing = `cat seeing.out`}" | xpaset timDIMM regions')
       os.system('echo "image;text 290 5 # text={R0 = `cat r0.out` cm}" | xpaset timDIMM regions')

       #this is needed for the ELS viewer
       os.system("date +'%Y-%m-%dT%H:%M:%S%z' >> seeing.out")
       os.system("mv seeing.out seeing.txt")
       #os.system("scp seeing.txt timdimm@timdimm:/Users/timdimm/Sites/")
       
       pass
   else:
        print "FAIL!"
        os.system('echo "image;text 125 5 # text={Unsuccessful Measurement}" | xpaset timDIMM regions')
        if os.path.isfile('centroids.dat'): os.remove('centroids.dat')
        if os.path.isfile('seeing.out'): os.remove('seeing.out')
