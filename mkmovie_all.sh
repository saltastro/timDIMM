#!/bin/sh

x=1; for i in `ls *.jpg`; do counter=$(printf %03d $x); ln -sf "$i" img"$counter".jpg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i img%03d.jpeg complete_anim.webm
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i img%03d.jpeg complete_anim.mp4
