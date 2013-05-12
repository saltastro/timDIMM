#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

s = GTO900.new()

s.clear
ra = s.ra
dec = s.dec

ra_deg = hms2deg(ra)
dec_deg = hms2deg(dec)

new_ra = ra_deg + 6.0
s.set_center_rate(200)
s.move('e')
loop {
  r = s.ra
  d = s.dec
  az = s.az
  alt = s.alt

  puts "At RA = %s, Dec = %s, Alt = %s, Az = %s" % [r, d, alt, az]

  d_ra = new_ra - hms2deg(r)

  puts "\t %f degrees to go in RA..." % [d_ra]
  if d_ra.abs < 1.0/60.0
    s.clear
    s.halt('e')
    puts "Done slewing."
    break
  end
  sleep(1)
}

s.close
