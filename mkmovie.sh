#!/bin/sh

cd /Library/WebServer/Documents/skycam/Data
x=1; for i in `ls *.jpg | tail -200`; do counter=$(printf %03d $x); ln -sf "$i" img"$counter".jpeg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i img%03d.jpeg latest_anim.webm
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i img%03d.jpeg latest_anim.mp4
