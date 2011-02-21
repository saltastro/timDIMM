#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

s = GTO900.new('massdimm', 7001)

s.clear
r = s.ra
d = s.dec
az = s.az
alt = s.alt
side = s.pier?

puts "At RA = %s, Dec = %s, Alt = %s, Az = %s, on the %s side of the pier" % [r, d, alt, az, side]

s.close
