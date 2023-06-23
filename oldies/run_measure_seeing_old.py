#!/usr/bin/env python

import os, shutil
import datetime 

import ox_wagon
import pick_star
from find_boxes import find_boxes
from guide_gto900 import guide_gto900
from pygto900 import GTO900, status, park_position, airmass
from spiral_search_gto900 import spiralsearch
import time
import sys
from astropy.coordinates import Angle

old_star = None
repeat = 1
niter = 15

spiral_log = '/home/massdimm/spiral.log'


def print_telescope_info(s):
    '''
    Print the telescope information
    '''
    print 'RA    :  %s' %s['ra'].to_string()
    print 'DEC   :  %s' %s['dec'].to_string()
    print 'LST   :  %s' %s['lst'].to_string()
    print 'HA    :  %s' %s['ha'].to_string()
    print 'ALT   :  %0.2f' %s['alt'].deg
    print 'AZ    :  %0.2f' %s['az'].deg
    print 'PIER  :  %s' %s['pier']

    return

def telescope_info(g):
    '''A method to monitor the telescope position while measuring the seeing
    ---
    If the telescope is in an compromising position, set a flag to stop measure
    seeing and try and point to a different star. This way 
    '''
    warn = False

    try:
        alt = Angle('%s degree' % g.alt())
    except ValueError:
        time.sleep(1)
        try:
            alt = Angle('%s degree' % g.alt())
        except ValueError:
            time.sleep(2)
            alt = Angle('%s degree' % g.alt())
    try:
        az = Angle('%s degree' % g.az())
    except ValueError:
        time.sleep(1)
        try:
            az = Angle('%s degree' % g.az())
        except ValueError:
            time.sleep(2)
            az = Angle('%s degree' % g.az())
    
    pier = g.pier().strip().lower()

    try:
        lst = Angle('%s hour' %g.lst())
    except ValueError:
        time.sleep(1)
        try:
            lst = Angle('%s hour' %g.lst())
        except ValueError:
            time.sleep(2)
            lst = Angle('%s hour' %g.lst())

    try:
        ra = Angle('%s hour' %g.ra())
    except ValueError:
        time.sleep(1)
        try:
            ra = Angle('%s hour' %g.ra())
        except ValueError:
            time.sleep(2)
            ra = Angle('%s hour' %g.ra())
    try:
        dec = Angle('%s degrees' %g.dec())
    except ValueError:
        time.sleep(1)
        try:
            dec = Angle('%s degrees' %g.dec())
        except ValueError:
            time.sleep(2)
            dec = Angle('%s degrees' %g.dec())
    
    
    ha = lst - ra

    scope = {}
    scope['alt'] = alt
    scope['az'] = az
    scope['pier'] = pier
    scope['lst'] = lst
    scope['ha'] = ha
    scope['ra'] = ra
    scope['dec'] = dec 

    if (pier == 'west') and (ha > Angle('00:40:00.0 hour')):
        warn = True
        if warn:
            os.system('rm current_object')
        print '***************************************************************'    
        print 'WARNING: Telescope could run into the pier'
        print '         Removed current object, expecting a repoint to target'
        print 'Check that it slews to the east side of the pier'
        print '**************************************************************'
    
    if (pier == 'west') and (ha > Angle('00:45:00.0 hour')):
        print '!!!************************************!!!'
        print 'The telescope is too close to the pier'
        print 'Stopping the telescope and parking it'
        print 'There probably is no other candidate star'
        print 'at the moment, so please wait a while'
        print 'before measureing the seeing again'
        print '******************************************'    
        g.haltall()
        park_position(g)
        time.sleep(45)
        g.park_mode()
        sys.exit()
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
        # set the telescope tracking rate to sideal rate
        g.select_tracking_rate('2')
        warn, scope = telescope_info(g)
        print '----------------------------------------'
        print 'WARNING:', warn
        print 'Telescope info:'
        print scope
        print
        print '----------------------------------------'
        print
        if scope['alt'] <= Angle('30 degree'):
           print '!!!WARNING: Telescope is at an altitude lower than 30 degrees !!!'
           print 'Seeing measurements will not start'
           print 'YOU MAY WANT TO CHECK THE TELESCOPE ALIGNMENT AND POINTING BEFORE STARTING MEASUREMENTS'
           g.park_mode()
           exit()
        else:
           print 'Telescope position checked'

        #pick the star
        try:
           pick_star.pick_star(g, scope)
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
