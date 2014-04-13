#!/usr/bin/env python

import os, shutil
import datetime 

import ox_wagon
import pick_star
from find_boxes import find_boxes
from guide_gto900 import guide_gto900

old_star = None

while True:
   #kill any existing running camera programs
   os.system('pkill ave_frames')
   os.system('pkill measure_seeing')

   #Make sure the ox wagon is open
   ox=ox_wagon.OxWagon()
   ox=ox.open()

     

   #pick the star
   try:
      pick_star.pick_star()
   except Exception, e:
      print Exception
      print 'Could not pick new star because %s' % e
      os.system('./pygto900.py init')
      pass


   #check to see if the star is available
   os.system('./ave_frames 10 \!center.fits')
   nstars = find_boxes('center.fits')

   if nstars < 2:
       os.system('./spiral_search_gto900.py')
       os.system('./pygto900.py sync')
       os.system('./ave_frames 10 \!center.fits')
       nstars = find_boxes('center.fits')

   #start turbina running
   try:
       current_star=open('current_object').read().strip()
   except:
       old_star = None

   if (old_star is None) or (old_star != current_star):
      os.system('./run_turbina.py')
      old_star = current_star
  
   #display star and log information
   os.system('cat center.fits | xpaset timDIMM fits')
   os.system('./pygto900.py log >> gto900.log')

   #measure star -- changed this down to 1000 from 10000
   os.system("./measure_seeing 1000 `tail -1 gto900.log | cut -d ' ' -f 7` `cat exptime`")

   # adjust the guiding
   guide_gto900()
 
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
       os.system("scp seeing.txt timdimm@timdimm:/Users/timdimm/Sites/")
       
       pass
   else:
        print "FAIL!"
        os.system('echo "image;text 125 5 # text={Unsuccessful Measurement}" | xpaset timDIMM regions')
        if os.path.isfile('centroids.dat'): os.remove('centroids.dat')
        if os.path.isfile('seeing.out'): os.remove('seeing.out')
