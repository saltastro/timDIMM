#!/usr/bin/env ruby

require 'rubygems'
gem 'nokogiri'
require 'nokogiri'
require 'open-uri'

module Weather

  def salt
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

  def wasp
    doc = Nokogiri::HTML(open("http://swaspgateway.suth/"))
    wx = Hash.new
    wx["Sky"] = doc.xpath("//table")[0].xpath("//td")[10].content
    wx["T - DP"] = doc.xpath("//table")[0].xpath("//td")[9].content.to_f
    wx["RH"] = doc.xpath("//table")[0].xpath("//td")[8].content.to_f
    wx["Temp"] = doc.xpath("//table")[0].xpath("//td")[7].content.to_f
    wx["Wind dir"] = doc.xpath("//table")[0].xpath("//td")[6].content
    wx["Wind speed"] = doc.xpath("//table")[0].xpath("//td")[5].content.to_f
    wx["Rain"] = doc.xpath("//table")[0].xpath("//td")[4].content
    wx["UT"] = doc.xpath("//table")[0].xpath("//td")[3].content.chomp
    return wx
  end

  def ness
    doc = Nokogiri.HTML(open("http://ystar1.suth/weather_log.php"))
    wx = Hash.new
    wx["SAST"] = doc.xpath("//table")[13].xpath("//td")[53].content
    wx["RH"] = doc.xpath("//table")[13].xpath("//td")[54].content.to_f
    wx["Temp"] = doc.xpath("//table")[13].xpath("//td")[58].content.to_f
    wx["Wind speed"] = doc.xpath("//table")[13].xpath("//td")[59].content.to_f*3.6
    wx["Wind dir"] = doc.xpath("//table")[13].xpath("//td")[60].content.to_f
    return wx
  end

  def grav
    kan11 = Nokogiri.HTML(open("http://sg1.suth/tmp/kan11.htm"))
    kan16 = Nokogiri.HTML(open("http://sg1.suth/tmp/kan16.htm"))
    wx = Hash.new
    wx["SAST"] = kan11.xpath("//td")[12].content
    wx["Temp"] = kan11.xpath("//td")[14].content.to_f
    wx["RH"] = kan11.xpath("//td")[15].content.to_f
    wx["Wind dir"] = kan16.xpath("//td")[13].content.to_i
    wx["Wind speed"] = kan16.xpath("//td")[14].content.to_f*3.6
    return wx
  end

end

if $0 == __FILE__
  include Weather
  wx = eval ARGV[0]
  wx.keys.each { |k|
    puts "%15s %20s" % [k, wx[k]]
  }
end
