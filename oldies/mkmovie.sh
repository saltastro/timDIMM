#!/bin/bash

cd /Library/WebServer/Documents/skycam/Data
x=1; for i in `ls *.jpg | tail -200`; do counter=$(printf %03d $x); ln -sf "$i" img"$counter".jpeg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -q:v 0 -f image2 -i img%03d.jpeg latest_anim.mp4
/opt/local/bin/ffmpeg -i latest_anim.mp4 -y -minrate 2M -maxrate 2M -b:v 2M latest_anim.webm
rm img*.jpeg
