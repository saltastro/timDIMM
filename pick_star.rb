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
s.clear
s.clear
lst = s.lst
airmass = s.airmass.to_f
az = s.az.to_f
alt = s.alt.to_f
s.close
sleep(1)

# add logic here to avoid the weather mast
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

  # put plenty of sleeps in to make sure nothing trips...  
  puts "Should move. Best HR number is #{best_hr}"
  puts t.stop
  system("./gto900_hr.rb #{best_hr}")
  system("echo \"#{best_hr}\" > current_object")
  puts t.object(best_hr)
  sleep(3)
  system("./gto900_offset.rb s")
  sleep(3)
  system("./gto900_offset.rb w")
  sleep(1)
  t.background
  sleep(3)
  system("./gto900_hr.rb #{best_hr}")
  sleep(3)
  system("./spiral_search_gto900.py")
  sleep(3)
  system("./gto900_guide.rb")
  sleep(3)
  puts t.run

end

t.close
