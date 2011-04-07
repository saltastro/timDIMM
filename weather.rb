def salt_wx
  wx = IO.popen("curl -s http://www.salt.ac.za/~saltmet/weather.txt").readlines

  keys = wx[0].chomp.split("\t")
  latest = wx[-1].chomp.split("\t")
  recent = wx[-10].chomp.split("\t")
  first = wx[1].chomp.split("\t")

  now = Hash.new
  hour = Hash.new
  tenmin = Hash.new

  i = 0
  keys.each { |k|
    now[k] = latest[i]
    hour[k] = first[i]
    tenmin[k] = recent[i]
    i = i + 1
  }

  now["Delta DP"] = now["Dew Point"].to_f - hour["Dew Point"].to_f
  now["T - DP"] = now["Temp (2m)"].to_f - now["Dew Point"].to_f

  return now
end
