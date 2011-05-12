#!/bin/sh

# first handle timDIMM data
mkdir -p ../timDIMM_data/$1
rm -f centroids.dat
gzip -v data/centroids_*.dat
mv -f data/* ../timDIMM_data/$1
mv -f *.log seeing.dat ../timDIMM_data/$1
mv -f *.fits ../timDIMM_data/$1
/usr/bin/rsync -av ../timDIMM_data/20* nfs4::seeingdata/massdimm/.

# now rotate skycam data
mkdir -p /Library/WebServer/Documents/skycam/`date -v -1d +'%Y/%m%d'`/
cd /Library/WebServer/Documents/skycam/`date -v -1d +'%Y/%m%d'`/
/usr/bin/rsync -e ssh -av concam@concam:/cygdrive/c/Users/concam/Desktop/Images/* .
chmod go+r *
cd /Library/WebServer/Documents/skycam
/usr/bin/rsync -av 20* nfs4::seeingdata/skycam/.
ssh -n concam@concam rm /cygdrive/c/Users/concam/Desktop/Images/*
rm Data/*
