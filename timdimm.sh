#!/bin/sh

while [ 1 ]; do ./ave_frames 50 \!center.fits; ./find_boxes.py center.fits; ./measure_seeing 10000; ./lx200_log.py; ./lx200_guide.py; done
