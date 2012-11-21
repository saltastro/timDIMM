#!/bin/sh

. /Users/timdimm/.massauth

# first handle timDIMM data
mkdir -p ../timDIMM_data/$1
rm -f centroids.dat
gzip -v data/centroids_*.dat
mv -f data/* ../timDIMM_data/$1
./db_insert.py seeing.dat
mv -f *.log seeing.dat ../timDIMM_data/$1
mv -f *.fits ../timDIMM_data/$1
/usr/bin/rsync -av ../timDIMM_data/20* nfs4::seeingdata/massdimm/.
touch SYNCME

# now rotate skycam data
mkdir -p /Library/WebServer/Documents/skycam/`date -v -1d +'%Y/%m%d'`/
cd /Library/WebServer/Documents/skycam/`date -v -1d +'%Y/%m%d'`/
mv /Library/WebServer/Documents/skycam/Data/* .
chmod go+r *
cd /Library/WebServer/Documents/skycam
/usr/bin/rsync -av 20* nfs4::seeingdata/skycam/.

