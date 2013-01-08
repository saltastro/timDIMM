#!/bin/sh

while [ 1 ]; do 
    pkill ave_frames
    pkill measure_seeing
    ./ox_wagon.py OPEN
    ./pick_star.rb
    ./ave_frames 10 \!center.fits
    ./find_boxes.py center.fits
    cat center.fits | xpaset timDIMM fits
    ./gto900_log.rb >> gto900.log
    ./measure_seeing 10000 `tail -1 gto900.log | cut -d ' ' -f 8` `cat exptime`
    ./gto900_guide.rb
    TIME=`date -u '+%Y%m%d-%H%M%S'`
    if [[ -s seeing.out ]]; then
	mv centroids.dat data/centroids_$TIME.dat
	cd data
	../dimm_stats.py centroids_$TIME.dat
	cd ..
	./plot.gnu
	echo "image;text 25 5 # text={Seeing = `cat seeing.out`\"}" | xpaset timDIMM regions
	echo "image;text 290 5 # text={R0 = `cat r0.out` cm}" | xpaset timDIMM regions
	date +'%Y-%m-%dT%H:%M:%S%z' >> seeing.out
	mv seeing.out ~/Sites/seeing.txt
	./tpoint_gto.rb `cat current_object` >> pointing.log
    else
	echo "FAIL!"
	echo "image;text 125 5 # text={Unsuccessful Measurement}" | xpaset timDIMM regions
	rm centroids.dat
	rm seeing.out
    fi
    xpaset -p timDIMM saveimage png ds9.png
    mv ds9.png /Users/timdimm/Sites/images/.
done
