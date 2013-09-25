#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

ra = ARGV[0]
dec = ARGV[1]

ra_deg = hms2deg(ra)
dec_deg = hms2deg(dec)

rh, rm, rs = ra.split(':')
dd, dm, ds = dec.split(':')

s = GTO900.new()

s.clear
s.command_alt(rh.to_i, rm.to_i, rs.to_i)
s.command_az(dd.to_i, dm.to_i, ds.to_i)
s.slew

loop {
  r = s.ra
  d = s.dec
  az = s.az
  alt = s.alt

  puts "At RA = %s, Dec = %s, Alt = %s, Az = %s" % [r, d, alt, az]

  d_ra = 15.0*Math::cos(hms2deg(d)*Math::PI/180.0)*(hms2deg(r) - ra_deg)
  d_dec = hms2deg(d) - dec_deg

  puts "\t %f degrees to go in RA, %f degrees to go in Dec...." % [d_ra, d_dec]
  if d_ra.abs < 1.0/60.0 && d_dec.abs < 1.0/60.0
    puts "Done slewing."
    break
  end
  sleep(1)
  break
}

s.close
