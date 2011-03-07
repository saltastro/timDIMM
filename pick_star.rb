#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'
require 'turbina'

s = GTO900.new('massdimm', 7001)
t = Turbina.new

lst = s.lst
airmass = s.airmass
s.close

if airmass < 1.5
  puts "Fine to stay here."
else 
  best_hr = best_star(lst)
  puts "Should move. Best HR number is #{best_hr}"
  puts t.stop
  `./gto900_hr.rb #{best_hr}`
  puts t.object(best_hr)
  `./spiral_search_gto900.py`
  puts t.run
end

t.close
