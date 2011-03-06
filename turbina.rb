#!/usr/bin/env ruby

##### this is an implementation of the supervisor protocol used by turbina

require 'timeout'
require 'socket'

### turbina routines
class Turbina
  def initialize
    @port = sockopen('massdimm.suth', 16007)
  end

  # wrapper for opening socket and dealing with timeouts
  def sockopen(host, port)
    socket = nil
    status = nil
    timeout = 5.0
    begin
      timeout(5) {
        socket = TCPSocket.open(host, port)
      }
    rescue TimeoutError
      status = "Timeout"
      return nil
    rescue Errno::ECONNREFUSED
      status = "Refusing connection"
      return nil
    rescue => why
      status = "Error: #{why}"
      return nil
    end
    return socket
  end

  def close
    @port.close
    @port = nil
  end

  def read
    @port.gets.split('=')[1]
  end

  def command(string)
    @port.send("1001 #{string}\r\n", 0)
  end

  def get(cmd)
    command("get #{cmd}")
    return read
  end

  def stop
    command("stop")
    wait = read.to_i
    puts "Waiting #{wait} sec for turbina to finish...."
    sleep(wait)
    return read
  end

  def stop_now
    command("stop now")
    wait = read.to_i
    puts "Waiting #{wait} sec for turbina to finish...."
    sleep(wait)
    return read
  end

  def status
    command("get status")
    return read
  end

  def run
    command("run")
    wait = read.to_i
    return wait
  end

  def background
    command("run scen1")
    wait = read.to_i
    puts "Running background measurement...."
    sleep(wait)
    puts "....done."
    return read
  end

  def object(star)
    command("set object=#{star.to_s}")
    return read
  end

  def park
    command("park")
    wait = read.to_i
    puts "Parking turbina...."
    sleep(wait)
    puts "...done"
    return read
  end

  def init
    command("init")
    return read
  end

end

if $0 == __FILE__
  t = Turbina.new
  cmd = "t." + ARGV[0]
  if ARGV[1]
    cmd = cmd + '(' + ARGV[1] + ')'
  end
  out = eval cmd
  puts "Turbina: " + out
end
