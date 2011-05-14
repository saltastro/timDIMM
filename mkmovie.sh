#!/bin/sh

cd /Library/WebServer/Documents/skycam/Data
x=1; for i in `ls *.JPG | tail -200`; do counter=$(printf %03d $x); ln -sf "$i" img"$counter".jpg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i img%03d.jpg latest_anim.mov
