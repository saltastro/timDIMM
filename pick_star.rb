#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'
require 'turbina'
require 'timeout'

sleep(2)
s = GTO900.new('massdimm', 7001)
t = Turbina.new

best_hr = ""

s.clear
lst = s.lst
airmass = s.airmass
az = s.az
alt = s.alt
s.close
sleep(1)

az = hms2deg(az)
alt = hms2deg(alt)

if airmass < 1.5 && !(alt < 75.0 && az > 285.0 && az < 295.0)
  puts "Fine to stay here."
  stat = t.status
  if stat =~ /READY/
    puts t.run
  end
else 

  best_hrs = best_star(lst)
  if best_hr == best_hrs[0]
    best_hr = best_hrs[1]
  else
    best_hr = best_hrs[0]
  end
  
  puts "Should move. Best HR number is #{best_hr}"
  puts t.stop
  system("./gto900_hr.rb #{best_hr}")
  system("echo \"#{best_hr}\" > current_object")
  puts t.object(best_hr)
  system("./gto900_offset.rb w")
  t.background
  system("./gto900_hr.rb #{best_hr}")
  sleep(3)
  system("./spiral_search_gto900.py")
  system("./gto900_guide.rb")
  puts t.run

end

t.close
