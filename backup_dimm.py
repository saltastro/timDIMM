#!/usr/bin/env python
import sys
import os
import glob
import shutil


def move_files(names, arch_dir):
    """Move a group of files"""
    infiles=glob.glob(names)
    for f in infiles: shutil.move(f, arch_dir)

def backup_dimm(obsdate, data_dir='/home/massdimm/data/massdimm/', home_dir='/home/massdimm/timDIMM/'):
    """Prepare and back up the DIMM data

    """

    #move to the directory with all of the scripts
    os.chdir(home_dir)

    #check to see if the directories are ready
    obsdate=str(obsdate)
    if not os.path.isdir(data_dir+obsdate[0:4]): os.mkdir(data_dir+obsdate[0:4])
    arch_dir = '%s%s/%s' % (data_dir, obsdate[0:4], obsdate[4:8])
    if not os.path.isdir(arch_dir): os.mkdir(arch_dir)

    #load data to the database
    os.system('./db_insert.py seeing.dat')

    #compress existing data
    os.system('gzip -v data/centroids_*.dat')
 
    #move the files
    move_files('data/*', arch_dir)
    move_files('*.fits', arch_dir)
    move_files('*.log', arch_dir)
    shutil.move('seeing.dat', arch_dir)

    #clean up the results
    if os.path.isfile('centroid.dat'): os.remove('centroid.dat')

if __name__=='__main__':
   import datetime as dt
 
   if len(sys.argv)==2:
      obsdate = sys.argv[1]
   else:
      obsdate = dt.datetime.now() - dt.timedelta(seconds=12*3600.)  
      obsdate = obsdate.strftime('%Y%m%d')
      print obsdate
 
   backup_dimm(obsdate)
