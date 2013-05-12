#!/bin/bash

cd /Library/WebServer/Documents/skycam/Data
x=1; for i in `ls *.jpg | tail -200`; do counter=$(printf %03d $x); ln -sf "$i" img"$counter".jpeg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -g 120 -level 216 -qmax 42 -qmin 10 -rc_buf_aggressivity 0.95 -vb 2M -f image2 -i img%03d.jpeg latest_anim.webm
/opt/local/bin/ffmpeg -y -r 10 -qscale 0 -f image2 -i img%03d.jpeg latest_anim.mp4
rm img*.jpeg
