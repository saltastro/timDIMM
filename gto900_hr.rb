#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

cat = hr_catalog

hr = ARGV[0]

ra_deg = hms2deg(cat[hr][:ra])
dec_deg = hms2deg(cat[hr][:dec])

#s = GTO900.new('massdimm', 7001)

#s.clear
#s.slew_HR(hr)

puts "Slewing to HR #{hr} (#{cat[hr][:name]}) at RA = #{cat[hr][:ra]} Dec = #{cat[hr][:dec]}......"

#loop {
# r = s.ra
#   d = s.dec
#   az = s.az
#   alt = s.alt

#   puts "At RA = %s, Dec = %s, Alt = %s, Az = %s" % [r, d, alt, az]

#   d_ra = 15.0*Math::cos(hms2deg(d)*Math::PI/180.0)*(hms2deg(r) - ra_deg)
#   d_dec = hms2deg(d) - dec_deg

#   puts "\t %f degrees to go in RA, %f degrees to go in Dec...." % [d_ra, d_dec]
#   if d_ra.abs < 1.0/60.0 && d_dec.abs < 1.0/60.0
#     puts "Done slewing."
#     break
#   end
#   sleep(1)
# }

# s.close
