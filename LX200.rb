##### this is a ruby implementation of the LX200 serial command protocol

require 'serialport.so'

### LX200 routines
class LX200
  def initialize(port)
    @port = SerialPort.new(port, 9600, 8, 1, SerialPort::NONE)
    @rates = Hash.new

    # map english rate names to those used by the LX200
    @rates['Center'] = 'C'
    @rates['Find'] = 'M'
    @rates['Max'] = 'S'
    @rates['Guide'] = 'G'
  end

  # read output from the LX200.  the LX200 usually outputs a '#'
  # terminated string, but not always....
  def read_LX200
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
    return string + "\0"
  end

  # send a command off to the LX200
  def command(string)
    @port.write(string)
    sleep(0.1)
  end

  # command the LX200 to auto-align itself.  this is one of those
  # commands that does not output a '#' terminated string.  it also
  # doesn't appear to do exactly what the auto align command does from
  # the hand paddle.  this command goes through the normal motions of
  # finding north, level, tip, and tilt, but doesn't seem to sync to
  # GPS or prompt for alignment stars. 
  def auto_align
    command("#:Aa#")
    result = @port.read(1)
    if result.to_i == 1
      return "Automatic Alignment Successful.\n"
    else
      return "Automatic Alignment Failed.\n"
    end
  end

  # query alignment mode (also doesn't return '#' terminated string)
  def align_query
    command("\x06")
    result = @port.read(1)
    if result =~ /A/
      return "AltAz"
    elsif result =~ /L/
      return "Land"
    else
      return "Polar"
    end
  end

  # set telescope to land alignment mode
  def align_land
    command("#:AL#")
  end

  # set telescope to polar alignment mode
  def align_polar
    command("#:AP#")
  end

  # set telescope to AltAz alignment mode
  def align_altaz
    command("#:AA#")
  end

  # set alt/dec antibacklash to 'num'
  def antibacklash_alt(num)
    if num > 99
      num = 99
    end
    if num < 0
      num = 0
    end
    num = sprintf("%02d", num)
    command("#:BA#{num}#")
  end

  # set az/ra antibacklash to 'num'
  def antibacklash_az(num)
    if num > 99
      num = 99
    end
    if num < 0
      num = 0
    end
    num = sprintf("%02d", num)
    command("#:BZ#{num}#")
  end

  # increase reticle brightness
  def increase_reticle_brightness
    command("#:B+#")
  end

  # decrease reticle brightness
  def decrease_reticle_brightness
    command("#:B-#")
  end

  # set reticle flash rate to 'n' where n = 0..9
  def reticle_flash_rate(n)
    if n >= 0 && n <= 9
      command("#:B#{n}#")
    end
  end

  # set reticle duty flash cycle to 'n' where n = 0..15
  def reticle_flash_duty_cycle
    if n >= 0 && n <= 15
      command("#:BD#{n}#")
    end
  end

  # check if the LX200 is slewing
  def is_slewing?
    command("#:D#")
    # result = @port.read(1)
    result = read_LX200 
    if result =~ /\x7F/
      return true
    else
      return false
    end
  end

  # command the LX200 to sync its RA and Dec to those of the current object
  def sync
    command("#:CM#")
    return read_LX200
  end

  # command LX200 to sync to current lunar selenographic coordinates
  def sync_lunar
    command("#:CL#")
    return read_LX200
  end

  # turn accessory panel power on
  def accessory_panel_power_on
    command("#:f+#")
  end

  # turn accessory panel power off
  def accessory_panel_power_off
    command("#:f-#")
  end

  # read the OTA temperature.
  # this command is VERY DANGEROUS!  it sometimes works, but if it does not, 
  # then it seems to completely lock up mount communications and requires
  # a power cycle to clear up. 
  def temp
    command("#:fT#")
    read_LX200.to_f
  end

  # set the speed of the electronic focuser
  def focus_speed(speed)
    if speed < 1
      speed = 1
    end
    if speed > 4
      speed = 4
    end
    command("#:F#{speed}#")
  end

  # command the focuser to move inward (toward the primary)
  def focus_in
    command("#:F+#")
  end

  # command the focuser to move outward (away from the primary)
  def focus_out
    command("#:F-#")
  end

  # halt all focuser motion
  def focus_halt
    command("#:FQ#")
  end

  # turn on the GPS
  def gps_on
    command("#:g+#")
  end

  # turn off the GPS
  def gps_off
    command("#:g-#")
  end

  # get NMEA string
  def get_NMEA
    command("#:gps#")
    nmea = read_LX200
    return nmea
  end

  # turn on gps and update system time from it
  def gps_update
    command("#:gT#")
    result = @port.read(1)
    if result =~ /'0'/
      return "GPS update interrupted or timed out."
    else
      return "GPS update successful."
    end
  end

  # read the current altitude from the LX200
  def alt
    command("#:GA#")
    string = read_LX200
    format = ""
    string.scan(/(.)(\d+)\xDF(\d+):(\d+)/) { |sign, d, m, s|
      format = sign + d + ":" + m + ":" + s
    }
    return format
  end

  # read the current azimuth from the LX200
  def az
    command("#:GZ#")
    string = read_LX200
    format = ""
    string.scan(/(\d+)\xDF(\d+):(\d+)/) { |d, m, s|
      format = d + ":" + m + ":" + s
    }
    return format
  end
    
  # read local time from the LX200 in 12 hr format
  def local_time_12hr
    command("#:Ga#")
    return read_LX200
  end

  # read local time from the LX200 in 24 hr format
  def local_time_24hr
    command("#:GL#")
    return read_LX200
  end

  # read current date from the LX200
  def local_date
    command("#:GC#")
    return read_LX200
  end

  # get calendar format from LX200. returns 12 or 24.
  def calendar_format
    command("#:Gc#")
    return read_LX200
  end

  # read the current declination from the LX200
  def dec
    command("#:GD#")
    string = read_LX200
    format = ""
    string.scan(/(.)(\d+)\xDF(\d+):(\d+)/) { |sign, d, m, s|
      format = sign + d + ":" + m + ":" + s
    }
    return format
  end

  # read the target declination of the current object in memory
  def obj_dec
    command("#:Gd#")
    string = read_LX200
    format = ""
    string.scan(/(.)(\d+)\xDF(\d+):(\d+)/) { |sign, d, m, s|
      format = sign + d + ":" + m + ":" + s
    }
    return format
  end

  # get UTC offset from LX200
  def get_UTC_offset
    command("#:GG#")
    return read_LX200
  end

  # get current site longitude
  def get_longitude
    command("#:Gg#")
    string = read_LX200
    string.scan(/(.)(\d+)\xDF(\d+)/) { |sign, d, m|
      format = sign + d + ":" + m + ":00"
    }
    return format
  end

  # get current site latitude
  def get_latitude
    command("#:Gt#")
    string = read_LX200
    string.scan(/(.)(\d+)\xDF(\d+)/) { |sign, d, m|
      format = sign + d + ":" + m + ":00"
    }
    return format
  end

  # get telescope firmware date
  def get_firmware_date
    command("#:GVD#")
    return read_LX200
  end

  # get telescope firmware number
  def get_firmware_number
    command("#:GVN#")
    return read_LX200
  end

  # get telescope firmware name
  def get_firmware_name
    command("#:GVP#")
    return read_LX200
  end

  # get telescope firmware time
  def get_firmware_time
    command("#:GVT#")
    return read_LX200
  end

  # read the current RA from the LX200
  def ra
    command("#:GR#")
    return read_LX200
  end

  # read the target RA of the current object in memory
  def obj_ra
    command("#:Gr#")
    return read_LX200
  end

  # read the current local sidereal time
  def lst
    command("#:GS#")
    return read_LX200
  end

  # command the LX200 to wake up from a sleep state
  def wakeup
    command("#:hW#")
  end

  # command the LX200 to go to sleep
  def snooze
    command("#:hN#")
  end

  # toggle time format
  def toggle_time_format
    command("#:H#")
  end

  # initialize the telescope.  causes the telescope to cease operations
  # and restart at its power-on initialization
  def init_scope
    command("#:I#")
  end

  # command the LX200 to slew to the target alt and az
  def altaz_slew
    command("#:MA#")
    result = @port.read(1)
    if result.to_i == 1
      return "Problem performing alt/az slew.\n"
    else
      return "Alt/az slew successful.\n"
    end
  end

  # command the LX200 to slew to the target RA and Dec
  def slew
    command("#:MS#")
    result = @port.read(1)
    if result.to_i == 0
      return "Slewing...."
    else
      return read_LX200
    end
  end

  # command the LX200 to move in the given direction at the current slew rate
  def move(dir)
    if dir == "e" || dir == "n" || dir == "s" || dir == "w"
      command("#:M#{dir}#")
    end
  end

  # command the LX200 to stop motion in the given direction
  def halt(dir)
    if dir == "e" || dir == "n" || dir == "s" || dir == "w"
      command("#:Q#{dir}#")
    end
  end

  # command the LX200 to halt all mount motion
  def haltall
    command("#:Q#")
  end

  # toggle pointing precision mode
  def pointing_prec
    command("#:P#")
  end

  # toggle precision of position readouts
  def position_prec
    command("#:U#")
  end

  # set slew rate to 'center' (2nd slowest == 0.5 arcmin/sec)
  def center_rate
    command("#:RC#")
  end

  # set slew rate to 'guide' (slowest, adjustable via set_guide_rate method)
  def guide_rate
    command("#:RG#")
  end

  # set slew rate to 'find' (2nd fastest == 180 arcmin/sec)
  def find_rate
    command("#:RM#")
  end

  # set slew rate to 'max' (fastest == 480 arcmin/sec)
  def max_rate
    command("#:RS#")
  end

  # set slew rate to 'r'
  def rate(r)
    command("#:R#{@rates[r]}#")
  end

  # set RA slew rate to 'rate' degrees/sec
  def ra_rate(rate)
    command("#:RA#{rate}#")
  end

  # set Dec slew rate to 'rate' degrees/sec
  def dec_rate(rate)
    command("#:RE#{rate}#")
  end

  # set both RA and Dec slew rates to 'rate' degrees/sec
  def set_rate(rate)
    ra_rate(rate)
    dec_rate(rate)
  end

  # set guide rate to 'rate' arcsec/sec where 0 < rate <= 15.0417
  def set_guide_rate(rate)
    command("#:Rg#{rate}#")
  end

  # set target altitude
  def target_alt(alt)
    command("#:Sa#{alt}#")
    result = @port.read(1)
    return result
  end

  # set target azimuth
  def target_az(az)
    command("#:Sz#{az}#")
    result = @port.read(1)
    return result
  end

  # set target RA
  def target_ra(ra)
    command("#:Sr#{ra}#")
    result = @port.read(1)
    return result
  end

  # set target Dec
  def target_dec(dec)
    command("#:Sd#{dec}#")
    result = @port.read(1)
    return result
  end

end
