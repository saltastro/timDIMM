#!/usr/bin/env ruby

##### this is an implementation of the supervisor protocol used by turbina

require 'timeout'
require 'socket'

### turbina routines
class Turbina
  def initialize
    @status = "OFFLINE"
    @port = sockopen('massdimm.suth', 16007)
    status
  end

  # wrapper for opening socket and dealing with timeouts
  def sockopen(host, port)
    socket = nil
    msg = nil
    timeout = 5.0
    begin
      timeout(5) {
        socket = TCPSocket.open(host, port)
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
    return socket
  end

  def close
    @port.close if @port
    @port = nil
    @status = "OFFLINE"
  end

  def read
    if @port
      return @port.gets.split('=')[1]
    else
      @status = "OFFLINE"
      return nil
    end
  end

  def command(string)
    if @port
      @port.send("1001 #{string}\r\n", 0)
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
    command("run")
    resp = read
    if resp
      return resp
    else
      return @status
    end
  end

  def background
    command("run scen1")
    resp = read
    if resp
      wait = resp.to_i
      puts "Running background measurement...."
      sleep(wait+1)
      puts "....done."
      return read
    else
      return @status
    end
  end

  def object(star)
    command("set object=#{star.to_s}")
    return read
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
    get("flux")
  end

  def lprofile
    get("lprofile")
  end

  def integral
    get("integral")
  end

  def scind
    get("scind")
  end

  def bkgr
    get("bkgr")
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
end
