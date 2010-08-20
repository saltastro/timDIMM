#!/bin/sh

mkdir ../timDIMM_data/$1
rm -f centroids.dat
mv data/* ../timDIMM_data/$1
mv lx200.log seeing.dat ../timDIMM_data/$1
