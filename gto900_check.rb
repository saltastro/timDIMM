#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

s = GTO900.new('massdimm', 7001)

s.clear
r = s.ra
d = s.dec
az = s.az
alt = s.alt
lst = s.lst
secz = s.airmass
ha = sexagesimal(calc_ha(15*hms2deg(lst), 15*hms2deg(r))/15.0)
side = s.pier?

puts "At RA = %s, Dec = %s, HA = %s, Alt = %s, Az = %s, secz = %.2f, on the %s side of the pier" % [r, d, ha, alt, az, secz, side]

s.close
