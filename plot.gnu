#!/opt/local/bin/gnuplot
set xdata time
set timefmt x "%Y-%m-%d %H:%M:%S"
set format x "%H:%M"
set term png enhanced transparent font "/Library/Fonts/Arial.ttf,11"
set out "/Users/timdimm/Sites/images/seeing.png"
set xlabel "UT"
set ylabel "Seeing FWHM (arcsec)"
set yrange [0.0:5.0]
plot "seeing.dat" using 1:7 notitle
set term x11
#    EOF
