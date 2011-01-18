#!/bin/sh

mkdir -p ../timDIMM_data/$1
rm -f centroids.dat
gzip -v data/centroids_*.dat
mv -f data/* ../timDIMM_data/$1
mv -f lx200.log seeing.dat ../timDIMM_data/$1
mv -f *.fits ../timDIMM_data/$1
