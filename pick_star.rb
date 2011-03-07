#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

cat = hr_catalog

lst = 15*hms2deg("10:00:00")

cat.each { |star|

  r = 15*hms2deg(star[:ra])
  ha = sexagesimal(lst - r)

  cat[star][:ha] = ha

}

puts cat["3685"][:ha]

