#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'
require 'turbina'
require 'timeout'
require 'LX200/weather'

include Weather

def check_turbina(tb)
  if tb
    stat = "UNKNOWN"
    timeout(5) {
        stat = tb.status
    }
    if stat =~ /READY/
      puts tb.run
    end
  end
end

rh = 0.0

wx = Array.new
wx.push(salt)
wx.push(grav)

ngood = 0
sum = 0
wx.each { |w|
  if w
    sum = sum + w["RH"].to_f
    ngood = ngood + 1
  end
}

rh = sum/ngood

if rh == 0.0
  puts "\033[0;31mNo Humidity Readind ALERT: %.1f\033[0;39m" % rh
elsif rh < 85.0
  puts "\033[0;32mHumidity OK: %.1f\033[0;39m" % rh
else
  puts "\033[0;31mHigh Humidity ALERT: %.1f\033[0;39m" % rh
end

s = GTO900.new()

t = Turbina.new
#t = nil

if t
  temp = t.temperature
  puts "\033[0;32mMASS Temperature: %s\033[0;39m" % temp
  flux = t.flux
  puts "\033[0;32mMASS Flux: %s\033[0;39m" % flux
end

best_hr = ""

s.clear
s.clear
s.clear
lst = s.lst
side = s.pier?
airmass = s.airmass.to_f
az = s.az.to_f
alt = s.alt.to_f
s.close
sleep(1)

# add logic here to avoid the weather mast
if side =~ /East/ && airmass < 1.6 && !(alt < 75.0 && az > 285.0 && az < 300.0)
  puts "Fine to stay here."
  if t
    check_turbina(t)
  end
else 

  best_hrs = best_star(lst)
  current_hr = `cat current_object`.to_i
  
  if best_hrs[0] && best_hrs[1]
    if best_hrs[0].to_i == current_hr
      best_hr = best_hrs[1]
    else
      best_hr = best_hrs[0]
    end

    # put plenty of sleeps in to make sure nothing trips...  
    puts "Should move. Best HR number is #{best_hr}"
    if t
      puts t.stop
    end
    system("./gto900_hr.rb #{best_hr}")
    system("echo \"#{best_hr}\" > current_object")

    if t
      puts t.object(best_hr)
    end
    
    if t
      sleep(3)
      system("./gto900_offset.rb s")
      sleep(3)
      system("./gto900_offset.rb w")
      sleep(3)
      t.background
      sleep(5)
      system("./gto900_hr.rb #{best_hr}")
      sleep(5)
      system("echo '1.0e-3' > exptime")
      puts t.run
    end
    
  else
    puts "No better stars available.  Staying put...."
    if t
      check_turbina(t)
    end
  end

end

if t
  t.close
end
