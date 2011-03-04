#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

cat = hr_catalog

hr = ARGV[0]

s = GTO900.new('massdimm', 7001)

s.clear
r = s.ra.sub(':', ' ')
d = s.dec.sub(':', ' ')
l = s.lst.split(':')
lst = l[0] + ' ' + l[1]

cat_r = cat[hr][:ra].sub(':', ' ')
cat_d = cat[hr][:dec].sub(':', ' ')

puts cat_r + ' ' + cat_d + ' 0.0 0.0 J2000 ' + r + ' ' + d + ' ' + lst



