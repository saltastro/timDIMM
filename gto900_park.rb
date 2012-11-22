#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

s = GTO900.new()

s.clear
s.shutdown

az_c = 180.0
alt_c = 32.376

loop {
  az = s.az
  alt = s.alt

  puts "At Alt = %s, Az = %s" % [alt, az]

  d_az = hms2deg(az) - az_c
  d_alt = hms2deg(alt) - alt_c

  puts "\t %f degrees to go in Alt, %f degrees to go in Az..." % [d_alt, d_az]
  if d_az.abs < 1.0/2.0 && d_alt.abs < 1.0/2.0
    puts "Done parking."
    break
  end
  sleep(1)
}

s.close
