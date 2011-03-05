#!/bin/sh

mkdir -p ../timDIMM_data/$1
rm -f centroids.dat
gzip -v data/centroids_*.dat
mv -f data/* ../timDIMM_data/$1
mv -f *.log seeing.dat ../timDIMM_data/$1
mv -f *.fits ../timDIMM_data/$1
/usr/bin/rsync -av ../timDIMM_data/20* nfs4::seeingdata/massdimm/.
