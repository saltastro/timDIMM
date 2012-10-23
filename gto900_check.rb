#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

s = GTO900.new('localhost', 7001)

s.clear
s.clear
s.clear
r = s.ra
d = s.dec
az = s.az
alt = s.alt
lst = s.lst
secz = s.airmass
ha = sexagesimal(calc_ha(15*hms2deg(lst), 15*hms2deg(r))/15.0)
side = s.pier?

puts "At RA = %s, Dec = %s, HA = %s, LST = %s, Alt = %s, Az = %s, secz = %.2f, on the %s side of the pier" % [r, d, ha, lst, alt, az, secz, side]

s.close
