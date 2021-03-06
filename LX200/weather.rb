#!/usr/bin/env ruby

require 'rubygems'
gem 'nokogiri'
require 'nokogiri'
require 'open-uri'
require 'REXML/document'
require 'timeout'

module Weather

  def salt
    begin
      timeout(5) do
        doc = REXML::Document.new(open("http://icd.salt/xml/salt-tcs-icd.xml").read)
        doubles = doc.elements.to_a("//DBL")
        strings = doc.elements.to_a("//String")
        dbl = Hash.new
        str = Hash.new
        doubles.each { |d| 
          key = d.elements["Name"].text
          val = d.elements["Val"].text
          dbl[key] = val.to_f
        }
        strings.each { |s|
          key = s.elements["Name"].text
          val = s.elements["Val"].text
          str[key] = val
        }
        ntemps = 7
        temp = 0.0
        doc.elements.each("*/Cluster/Array/DBL/Val") { |e|
          temp = temp + e.text.to_f
        }
        temp = temp/ntemps
    
        wx = Hash.new
        wx["SAST"] = str["SAST"].split(' ')[1]
        wx["Date"] = str["SAST"].split(' ')[0]
        wx["Air Pressure"] = "%.1f" % (dbl["Air pressure"]*10.0)
        wx["Dewpoint"] = "%.2f" % dbl["Dewpoint"]
        wx["RH"] = "%.1f" % dbl["Rel Humidity"]
        wx["Wind Speed (30m)"] = "%.1f" % (dbl["Wind mag 30m"]*3.6)
        wx["Wind Speed (10m)"] = "%.1f" % (dbl["Wind mag 10m"]*3.6)
        wx["Wind Dir (30m)"] = "%.1f" % dbl["Wind dir 30m"]
        wx["Wind Dir (10m)"] = "%.1f" % dbl["Wind dir 10m"]
        wx["Temp"] = "%.1f" % temp
        t = temp - dbl["Dewpoint"]
        wx["T - DP"] = "%.1f" % t
        return wx
      end
    rescue Timeout::Error
      return nil
    rescue 
      return nil
    end
  end
  
  def salt_txt
    begin
      timeout(2) do
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
    rescue Timeout::Error
      return nil
    rescue
      return nil
    end
  end

  def wasp
    begin
      timeout(2) do
        doc = Nokogiri::HTML(open("http://swaspgateway.suth/"))
        wx = Hash.new
        wx["Lightning"] = doc.xpath("//table")[0].xpath("//td")[11].content
        wx["Sky"] = doc.xpath("//table")[0].xpath("//td")[10].content
        wx["T - DP"] = doc.xpath("//table")[0].xpath("//td")[9].content.to_f
        wx["RH"] = doc.xpath("//table")[0].xpath("//td")[8].content.to_f
        wx["Temp"] = doc.xpath("//table")[0].xpath("//td")[7].content.to_f
        wx["Wind Dir"] = doc.xpath("//table")[0].xpath("//td")[6].content
        wx["Wind Speed"] = doc.xpath("//table")[0].xpath("//td")[5].content.to_f
        wx["Rain"] = doc.xpath("//table")[0].xpath("//td")[4].content
        wx["UT"] = doc.xpath("//table")[0].xpath("//td")[3].content.chomp
        wx["Status"] = doc.xpath("//table")[0].xpath("//td")[32].content
        return wx
      end
    rescue Timeout::Error
      return nil
    rescue
      return nil
    end
  end

  def ness
    begin
      timeout(2) do
        doc = Nokogiri.HTML(open("http://ystar1.suth/weather_log.php"))
        wx = Hash.new
        wx["SAST"] = doc.xpath("//table")[13].xpath("//td")[53].content
        wx["RH"] = doc.xpath("//table")[13].xpath("//td")[54].content.to_f
        wx["Temp"] = doc.xpath("//table")[13].xpath("//td")[58].content.to_f
        wx["Wind Speed"] = doc.xpath("//table")[13].xpath("//td")[59].content.to_f*3.6
        wx["Wind Dir"] = doc.xpath("//table")[13].xpath("//td")[60].content.to_f
        return wx
        end
    rescue Timeout::Error
      return nil
    rescue
      return nil
    end
  end

  def grav
    begin
      timeout(2) do
        kan11 = Nokogiri.HTML(open("http://sg1.suth/tmp/kan11.htm"))
        kan16 = Nokogiri.HTML(open("http://sg1.suth/tmp/kan16.htm"))
        wx = Hash.new
        wx["UT"] = kan11.xpath("//td")[12].content.split(' ')[1]
        wx["Date"] = kan11.xpath("//td")[12].content.split(' ')[0]
        wx["Temp"] = kan11.xpath("//td")[14].content.to_f
        wx["RH"] = kan11.xpath("//td")[15].content.to_f
        wx["Wind Dir"] = kan16.xpath("//td")[13].content.to_i
        wx["Wind Speed"] = kan16.xpath("//td")[14].content.to_f*3.6
        return wx
      end
    rescue Timeout::Error
      return nil
    rescue
      return nil
    end
  end

end

if $0 == __FILE__
  include Weather
  wx = eval ARGV[0]
  if wx
    wx.keys.sort.each { |k|
      puts "%20s %25s" % [k, wx[k]]
    }
  else
    puts "No information received."
  end
end
