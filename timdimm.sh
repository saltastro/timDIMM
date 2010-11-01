#!/bin/sh

while [ 1 ]; do 
    ./ave_frames 50 \!center.fits
    ./find_boxes.py center.fits
    ./lx200_log.py
    ./measure_seeing 10000 `tail -1 lx200.log | cut -d ' ' -f 8`
    ./lx200_guide.py
    mv centroids.dat data/centroids_`date -u '+%Y%m%d-%H%M%S'`.dat
    ./plot.gnu
    echo "image;text 25 5 # text={Seeing = `cat seeing.out`\"}" | xpaset timDIMM regions
    echo "image;text 290 5 # text={R0 = `cat r0.out` cm}" | xpaset timDIMM regions
    xpaset -p timDIMM saveimage png ds9.png
    mv ds9.png /Users/timdimm/Sites/images/.
done
