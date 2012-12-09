#!/bin/sh

x=1; for i in `ls *.jpg`; do counter=$(printf %03d $x); ln -sf "$i" aimg"$counter".jpeg; x=$(($x+1)); done
/opt/local/bin/ffmpeg -y -r 10 -g 120 -level 216 -profile 0 -qmax 42 -qmin 10 -rc_buf_aggressivity 0.95 -vb 2M -f image2 -i aimg%03d.jpeg complete_anim.webm
/opt/local/bin/ffmpeg -y -r 10 -sameq -f image2 -i aimg%03d.jpeg complete_anim.mp4
rm aimg*.jpeg
