##### this is a ruby implementation of the Astro-Physics GTO900 serial command protocol

require 'timeout'
require 'socket'
require 'ast_utils'

### GTO900 routines
class GTO900
  def initialize(host, port)
    @port = sockopen(host, port)
    @catalog = hr_catalog
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

  # read output from the GTO900.  the GTO900 usually outputs a '#'
  # terminated string, but not always....
  def read_GTO900
    string = ""
    loop {
      char = @port.read(1)
      if char
	break if char =~ /#/
	string = string + char
      else 
	break
      end
    }
#    return string + "\0"
    return string
    clear
  end

  # check the boolean 1/0 returns from the mount
  def check_GTO900
    result = @port.read(1)
    clear
    return result
  end

  # send a command off to the GTO900
  def command(string)
    @port.send(string, 0)
  end

  # clear input buffer
  def clear
    command("#")
  end

  # set long format
  def long_format
    command("#:U#")
  end

  # set the offset from greenwich mean time
  def set_gmt_offset(hrs)
    command("#:SG #{hrs}#")
    return check_GTO900
  end
  
  # set the current longitude
  def set_longitude(d, m, s)
    str = "%d*%02d:%02d" % [d, m, s]
    command("#:Sg #{str}#")
    return check_GTO900
  end

  # set the current latitude
  def set_latitude(d, m, s)
    str = "%d*%02d:%02d" % [d, m, s]
    command("#:St #{str}#")
    return check_GTO900
  end

  # set current date (MM/DD/YY)
  def set_current_date
    time = Time.new
    ut = time.getutc
    date = ut.strftime("%m/%d/%Y")
    command("#:SC #{date}#")
    blah = read_GTO900
    return read_GTO900
  end

  # set local time (HH:MM:SS)
  def set_local_time
    time = Time.new
    str = time.strftime("%H:%M:%S")
    command("#:SL #{str}#")
    return check_GTO900
  end

  # get UTC offset from GTO900
  def get_UTC_offset
    command("#:GG#")
    string = read_GTO900
    sign, h, m, s, ds = string.scan(/(.)(\d+):(\d+):(\d+).(\d+)/)[0]
    return sign + h
  end

  # get current site longitude
  def get_longitude
    command("#:Gg#")
    string = read_GTO900
    sign, d, m, s = string.scan(/(.)(\d+)\*(\d+):(\d+)/)[0]
    output = sign + d + ":" + m + ":" + s
    return output
  end

  # get current site latitude
  def get_latitude
    command("#:Gt#")
    string = read_GTO900
    sign, d, m, s = string.scan(/(.)(\d+)\*(\d+):(\d+)/)[0]    
    output = sign + d + ":" + m + ":" + s
    return output
  end

  # get local time
  def get_local_time
    command("#:GL#")
    string = read_GTO900
    return string
  end

  # get LST
  def lst
    command("#:GS#")
    return read_GTO900
  end

  # read the current RA from the GTO900
  def ra
    command("#:GR#")
    return read_GTO900
  end

  # read the current declination from the GTO900
  def dec
    command("#:GD#")
    string = read_GTO900
    output = ""
    sign, d, m, s = string.scan(/(.)(\d+)\*(\d+):(\d+)/)[0]
    output = sign + d + ":" + m + ":" + s
    return output
  end

  # read the current altitude from the GTO900
  def alt
    command("#:GA#")
    string = read_GTO900
    output = ""
    sign, d, m, s = string.scan(/(.)(\d+)\*(\d+):(\d+)/)[0]
    output = sign + d + ":" + m + ":" + s
    return output
  end

  # calculate current GTO900 airmass
  def airmass
    a = alt
    ang = Math::PI*(90.0-hms2deg(a))/180.0
    return 1.0/Math::cos(ang)
  end

  # read the current azimuth from the GTO900
  def az
    command("#:GZ#")
    string = read_GTO900
    output = ""
    d, m, s = string.scan(/(\d+)\*(\d+):(\d+)/)[0]
    output = d + ":" + m + ":" + s
    return output
  end

  # command the GTO900 to slew to the target RA and Dec
  def slew
    command("#:MS#")
    result = @port.read(1)
    if result.to_i == 0
      return "Slewing...."
    else
      return read_GTO900
    end
  end

  # command the GTO900 to move in the given direction at 
  # the current guide or centering rate
  def move(dir)
    if dir == "e" || dir == "n" || dir == "s" || dir == "w"
      command("#:M#{dir}#")
    end
  end

  # command the GTO900 to move in the given direction at 
  # the current guide or centering rate 
  # for a given number of ms
  def move_ms(dir, ms)
    if dir == "e" || dir == "n" || dir == "s" || dir == "w"
      command("#:M#{dir}#{ms}#")
    end
  end

  # swap north-south buttons
  def swap_ns
    command("#:NS#")
  end

  # swap east-west buttons
  def swap_ew
    command("#:EW#")
  end

  # command the GTO900 to stop motion in the given direction
  def halt(dir)
    if dir == "e" || dir == "n" || dir == "s" || dir == "w"
      command("#:Q#{dir}#")
    end
  end

  # command the GTO900 to halt all mount motion
  def haltall
    command("#:Q#")
  end

  # select guide rate
  def select_guide_rate(rate='')
    if rate == '' || rate == '0' || rate == '1' || rate == '2'
      command("#:RG#{rate}#")
    end
  end

  # select centering rate
  def select_center_rate(rate='')
    if rate == '' || rate == '0' || rate == '1' || rate == '2' || rate == '3'
      command("#:RC#{rate}#")
    end
  end

  # set centering rate
  def set_center_rate(rate)
    if rate > 0 && rate < 256
      command("#:Rc#{rate}#")
    end
  end

  # select slew rate
  def select_slew_rate(rate='')
    if rate == '' || rate == '0' || rate == '1' || rate == '2'
      command("#:RS#{rate}#")
    end
  end

  # set slew rate
  def set_slew_rate(rate)
    if rate > 0 && rate <= 1200
      command("#:Rs#{rate}#")
    end
  end

  # select tracking rate
  def select_tracking_rate(rate='')
    if rate == '' || rate == '0' || rate == '1' || rate == '2' || rate == '9'
      command("#:RS#{rate}#")
    end
  end

  # set RA tracking rate
  def set_RA_rate(rate)
    command("#:RR #{rate}#")
  end

  # set Dec tracking rate
  def set_Dec_rate(rate)
    command("#:RD #{rate}#")
  end

  # set amount of Dec backlash compensation (in seconds)
  def set_Dec_backlash(sec)
    command("#:Bd 00*00:#{sec}#")
    return read_GTO900
  end

  # set amount of RA backlash compensation (in seconds)
  def set_RA_backlash(sec)
    command("#:Br 00:00:#{sec}#")
    return read_GTO900
  end

  # invoke parked mode
  def park_mode
    command("#:KA#")
  end

  # park off
  def park_off
    command("#PO:#")
  end

  # query pier
  def pier?
    command("#:pS#")
    return read_GTO900
  end

  # sync mount
  def sync
    command("#:CM#")
    return read_GTO900
  end

  # re-cal mount
  def recal
    command("#:CMR#")
    return read_GTO900
  end

  # define commanded RA
  def command_ra(h, m, s)
    str = "%02d:%02d:%02d" % [h,m,s]
    command("#:Sr #{str}#")
    return check_GTO900
  end

  def command_ra_raw(str)
    command("#:Sr #{str}#")
    return check_GTO900
  end
    
  # define commanded Dec
  def command_dec(d, m, s)
    str = "%d*%02d:%02d" % [d,m,s]
    command("#:Sd #{str}#")
    return check_GTO900
  end

  def command_dec_raw(str)
    command("#:Sd #{str}#")
    return check_GTO900
  end

  # define commanded Alt
  def command_alt(d, m, s)
    str = "%d*%02d:%02d" % [d,m,s]
    command("#:Sa #{str}#")
    return check_GTO900
  end

  # define commanded Az
  def command_az(d, m, s)
    str = "%d*%02d:%02d" % [d,m,s]
    command("#:Sz #{str}#")
    return check_GTO900
  end

  # increase reticle brightness
  def increase_reticle_brightness
    command("#:B+#")
  end

  # decrease reticle brightness
  def decrease_reticle_brightness
    command("#:B-#")
  end

  # command the focuser to move inward (toward the primary)
  def focus_in
    command("#:F+#")
  end

  # command the focuser to move outward (away from the primary)
  def focus_out
    command("#:F-#")
  end

  # focus fast
  def focus_fast
    command("#:FF#")
  end

  # focus slow
  def focus_slow
    command("#FS#")
  end

  # halt all focuser motion
  def focus_halt
    command("#:FQ#")
  end

  # get telescope firmware
  def get_firmware
    command("#:V#")
    return read_GTO900
  end

  # slew to star in HR catalog
  def slew_HR(hr)
    hr = hr.to_s
    ra = @catalog[hr][:ra]
    dec = @catalog[hr][:dec]
    command_ra_raw(ra)
    command_dec_raw(dec)
    slew
  end

  # startup procedure
  def startup
    clear
    long_format
#    set_RA_backlash(0)
#    set_Dec_backlash(0)
    set_local_time
    set_current_date
    set_latitude(-32, 22, 32)
    set_longitude(-20, 48, 30)
    set_gmt_offset(-2)
#    park_off
#    haltall
  end
  
  # shutdown procedure
  def shutdown
    clear
    command_az(180,0,0)
    command_alt(32,22,32)
    slew
    park_mode
  end

end
