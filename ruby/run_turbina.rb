#!/usr/bin/env ruby

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
#wx.push(grav)

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

t = Turbina.new
#t = nil

if t
  temp = t.temperature
  puts "\033[0;32mMASS Temperature: %s\033[0;39m" % temp
  flux = t.flux
  puts "\033[0;32mMASS Flux: %s\033[0;39m" % flux
end

if t
    check_turbina(t)
end

if tb
    stat = "UNKNOWN"
    timeout(5) {
        stat = tb.status
    }
    if stat =~ /READY/
        sleep(3)
        system("./pygto900.py nudge s")
        sleep(3)
        system("./pygto900.py nudge w")
        sleep(3)
        t.background
        sleep(5)
        system("./goto_hr.py")
        sleep(5)
        puts t.run
    end
end
    

if t
  t.close
end
