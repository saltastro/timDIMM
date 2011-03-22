#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'
require 'turbina'
require 'timeout'

sleep(2)
s = GTO900.new('massdimm', 7001)
t = Turbina.new

s.clear
lst = s.lst
s.clear
airmass = s.airmass
s.close
sleep(1)

if airmass < 1.5
  puts "Fine to stay here."
  stat = t.status
  if stat =~ /READY/
    puts t.run
  end
else 
  best_hr = best_star(lst)
  puts "Should move. Best HR number is #{best_hr}"
  puts t.stop
  system("./gto900_hr.rb #{best_hr}")
  system("echo \"#{best_hr}\" > current_object")
  puts t.object(best_hr)
  puts t.run
end

t.close
