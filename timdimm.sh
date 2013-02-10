#!/bin/sh
./ave_frames 20 \!center.fits
./find_boxes.py center.fits
cat center.fits | xpaset timDIMM fits
./measure_seeing_astelco 10000 $1 `cat exptime`
TIME=`date -u '+%Y%m%d-%H%M%S'`
if [[ -s seeing.out ]]; then
    mv centroids.dat data/centroids_$TIME.dat
    cd data
#    ../dimm_stats.py centroids_$TIME.dat
    cd ..
#    ./plot.gnu
    echo "image;text 25 5 # text={Seeing = `cat seeing.out`\"}" | xpaset timDIMM regions
    echo "image;text 290 5 # text={R0 = `cat r0.out` cm}" | xpaset timDIMM regions
    date +'%Y-%m-%dT%H:%M:%S%z' >> seeing.out
    mv seeing.out ~/Sites/seeing.txt
else
    echo "FAIL!"
    echo "image;text 125 5 # text={Unsuccessful Measurement}" | xpaset timDIMM regions
    rm centroids.dat
    rm seeing.out
fi
#xpaset -p timDIMM saveimage png ds9.png
#mv ds9.png ~/Sites/images/.
