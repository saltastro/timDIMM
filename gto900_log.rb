#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

scope = GTO900.new('localhost', 7001)

alt = scope.alt
az = scope.az
ra = scope.ra
dec = scope.dec
lst = scope.lst
localtime = scope.get_local_time

alt_d = hms2deg(alt)

airmass = 1.0/Math::sin(Math::PI*alt_d/180.0)

ha = sexagesimal(hms2deg(lst) - hms2deg(ra))

#output = open("gto900.log", "a")
#output.write(
#output.close()

puts "%s %s %s %s %s %s %s %.2f\n" % [localtime, lst, ra, dec, ha, alt, az, airmass]

scope.close

