#!/bin/sh

cd /Library/WebServer/Documents/skycam/Data
x=1; for i in `ls *.jpg`; do counter=$(printf %03d $x); ln -sf "$i" aimg"$counter".jpeg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -q:v 0 -f image2 -i aimg%03d.jpeg complete_anim.mp4
/opt/local/bin/ffmpeg -i complete_anim.mp4 -y -maxrate 2M -minrate 2M -b:v 2M complete_anim.webm
rm aimg*.jpeg
