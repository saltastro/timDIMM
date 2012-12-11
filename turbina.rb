#!/usr/bin/env ruby

##### this is an implementation of the supervisor protocol used by turbina

require 'timeout'
require 'socket'

### turbina routines
class Turbina
  def initialize
    @status = "OFFLINE"
    @port = sockopen('massdimm.suth', 16201)
    status
  end

  # method for wrapping a bit of code into a timeout
  def turbina_timeout(t, code)
    msg = nil
    result = nil
    begin
      timeout(t) {
        result = code.call
        @status = "ONLINE"
      }
    rescue TimeoutError
      msg = "Turbina Error: Timeout"
      @status = "OFFLINE"
    rescue Errno::ECONNREFUSED
      msg = "Turbina Error: Refusing connection"
      @status = "OFFLINE"
    rescue => why
      msg = "Turbina Error: #{why}"
      @status = "OFFLINE"
    end
    puts msg if msg
    return result
  end

  # wrapper for opening socket 
  def sockopen(host, port)
    socket = nil
    msg = nil
    timeout = 5.0
    socket = turbina_timeout(timeout, proc {TCPSocket.open(host, port)})
    return socket
  end

  def close
    turbina_timeout(1, proc {@port.close if @port})
    @port = nil
    @status = "OFFLINE"
  end

  def read
    if @port
      return turbina_timeout(5, proc {@port.gets.split('=')[1]})
    else
      @status = "OFFLINE"
      return nil
    end
  end

  def command(string)
    if @port
      turbina_timeout(5, proc {@port.send("1001 #{string}\r\n", 0)})
    else
      puts "No connection to turbina."
      @status = "OFFLINE"
      return nil
    end
  end

  def get(cmd)
    command("get #{cmd}")
    return read
  end

  def stop
    command("stop")
    resp = read
    if resp
      if resp =~ /PARKED/ || resp =~ /READY/
        @status = resp
        return resp
      else
        wait = read.to_i
        if wait > 1
          puts "Waiting #{wait} sec for turbina to finish...."
          sleep(wait+1)
          puts "...done"
          return read
        else
          return wait
        end
      end
    else
      return @status
    end
  end

  def stop_now
    command("stop now")
    sleep(1)
    resp = read
    if resp
      if resp =~ /PARKED/ || resp =~ /READY/
        @status = resp
        return resp
        else
        wait = read.to_i
        if wait > 1
          puts "Waiting #{wait} sec for turbina to finish...."
          sleep(wait+1)
          puts "...done"
          return read
          else
          return wait
        end
      end
      else
      return @status
    end

  end

  def status
    command("get status")
    resp = read
    if resp
      @status = resp
    end
    return @status
  end

  def run
    command("run scenario=100*N")
    resp = read
    if resp
      return resp
    else
      return @status
    end
  end

  def run_once
    command("run")
    resp = read
    if resp
      return resp
    else
      return @status
    end
  end

  def test_flux
    command("run flux")
    resp = read
    if resp
       wait = resp.to_i
       puts "Running flux measurement...."
       sleep(wait)
       puts "....done."
       read
       return flux
    else
       return @status
    end
  end

  def background
    command("run background")
    resp = read
    if resp
      wait = resp.to_i
      puts "Running background measurement...."
      sleep(30)
      puts "....done."
      read
      return flux
    else
      return @status
    end
  end

  def object(star)
    star = star.to_s
    dat = `grep "^ *#{star}" star.lst`.split(' ')
    str = [dat[0],
           dat[1..2].join('_'),
           dat[3..5],
           dat[6..7].join(),
           dat[8..12]].join(' ')
    puts str
    command("set object=\"#{str}\"")
    return read
  end

  def dtest
    command("run dtest")
    resp = read
    if resp
       wait = resp.to_i
       puts "Running detector test...."
       sleep(wait)
       puts "....done."
       return @port.gets
    else
       return @status
    end
  end

  def etest
    command("run etest")
    resp = read
    if resp
       wait = resp.to_i
       puts "Running exchange test...."
       sleep(wait)
       puts "....done."
       return @port.gets
    else
       return @status
    end
  end

  def stest
    command("run stest")
    resp = read
    if resp
       wait = resp.to_i
       puts "Running statistics test...."
       sleep(wait)
       puts "....done."
       return @port.gets
    else
       return @status
    end
  end

  def park
    unless @status =~ /PARKED/
      command("park")
      resp = read
      if resp
        wait = resp.to_i
        puts "Parking turbina...."
        sleep(wait)
        puts "...done"
        return read
      else
        return @status
      end
    end
  end

  def init
    command("init")
    resp = read
    if resp
      @status = resp
    end
    return @status
  end

  def flux
    command("get flux")
    if @port
        return @port.gets
    else
	return nil
    end
  end

  def data
    command("get data")
    return @port.gets
  end

  def temperature
    get("temperature")
  end

  def hv
    get("hv")
  end

  def set_hv(sw)
    if sw == "on" or sw == "off"
       command("set hv=#{sw}")
    end
  end

  def mirror
    get("mirror")
  end

  def illum
    get("illum")
  end

  def set_illum(sw)
    if sw == "on" or sw == "off"
       command("set illum=#{sw}")
    end
  end

  def light
    get("light")
  end

  def ident
    get("ident")
  end
  
  def reboot
    puts "Rebooting Turbina host computer....."
    system('ssh massdimm@massdimm.suth "sudo /sbin/shutdown -r now"')
    sleep(120)
    puts "....done."
    initialize
    return @status
  end

end

if $0 == __FILE__
  t = Turbina.new
  cmd = "t." + ARGV[0]
  if ARGV[1]
    cmd = cmd + '(' + ARGV[1] + ')'
  end
  out = eval cmd
  puts "Turbina: " + out.to_s
  t.close
end
