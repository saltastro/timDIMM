#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

cat = hr_catalog

hr = ARGV[0]

ra_deg = hms2deg(cat[hr][:ra])
dec_deg = hms2deg(cat[hr][:dec])

puts "Slewing to HR #{hr} (#{cat[hr][:name]}) at RA = #{cat[hr][:ra]} Dec = #{cat[hr][:dec]}......"

system("gto900_tpoint.rb #{cat[hr][:ra]} #{cat[hr][:dec]}")
