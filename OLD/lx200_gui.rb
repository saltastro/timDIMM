#!/usr/bin/env ruby

require 'libglade2'
require 'thread'
require 'timeout'
require 'serialport.so'

# set a global path to find scripts and stuff
if ENV['LX200']
  $path = ENV['LX200']
else
  $path = "/home/timdimm/MASSDIMM/timDIMM"
end

$:.push($path)

require 'LX200'

### define Paddle GUI
class Paddle

  def initialize(parent, scope)
    @mount_rates = [ "Max", "Find", "Center", "Guide" ]
    @focus_rates = [ "Slowest", "Slow", "Fast", "Fastest" ]

    @scope = scope
    @mutex = parent.mutex

    @glade = GladeXML.new("#{$path}/lx200/paddle.glade") {|handler| method(handler)}
    @menu = @glade.get_widget("RateMenu")
    @status = @glade.get_widget("PaddleStatus")
    @select = @glade.get_widget("Select")
    @select.active = 0
    @rate = @menu.active_iter.to_s
    @rateint = @menu.active
    @menu.active = 2
  end

  # routine to print to statusbar
  def report(text)
    @status.pop(0)
    @status.push(0, text)
  end

  def on_quit1_activate
    @glade.get_widget("PaddleWindow").destroy
  end

  def on_Select_changed
    if @select.active == 0
      @glade.get_widget("RateLabel").set_text("Slew Rate:  ")
      @glade.get_widget("Right").show
      @glade.get_widget("Left").show
      0.upto(3) { |pos|
	@menu.remove_text(pos)
	@menu.insert_text(pos, @mount_rates[pos])
      }
      @menu.active = 2
    else
      @glade.get_widget("RateLabel").set_text("Focus Rate:  ")
      @glade.get_widget("Right").hide
      @glade.get_widget("Left").hide
      0.upto(3) { |pos|
	@menu.remove_text(pos)
	@menu.insert_text(pos, @focus_rates[pos])
      }
      @menu.active = 2
    end
  end

  def on_RateMenu_changed
    @rate = @menu.active_iter.to_s
    @rateint = @menu.active
  end

  def halt
    Thread.new {
      @mutex.synchronize {
	if @select.active == 0
	  @scope.haltall
	else
	  @scope.focus_halt
	end
	report("Halted.")
      }
    }
  end

  def on_Up_pressed
    Thread.new {
      @mutex.synchronize {
	if @select.active == 0
	  @scope.rate(@rate)
	  @scope.move('n')
	  report("Moving North at #{@rate} rate.")
	else
	  @scope.focus_speed(@rateint.to_i + 1)
	  @scope.focus_in
	  report("Moving Focus in at #{@rate} rate.")
	end
      }
    }
  end

  def on_Down_pressed
    Thread.new {
      @mutex.synchronize {
	if @select.active == 0
	  @scope.rate(@rate)
	  @scope.move('s')
	  report("Moving South at #{@rate} rate.")
	else
	  @scope.focus_speed(@rateint.to_i + 1)
	  @scope.focus_out
	  report("Moving Focus out at #{@rate} rate.")
	end
      }
    }
  end

  # E and W appear to be revered on my LX200
  def on_Right_pressed
    Thread.new {
      @mutex.synchronize {
	@scope.rate(@rate)
	@scope.move('e')
	report("Moving West at #{@rate} rate.")
      }
    }
  end

  def on_Left_pressed
    Thread.new {
      @mutex.synchronize {
	@scope.rate(@rate)
	@scope.move('w')
	report("Moving East at #{@rate} rate.")
      }
    }
  end

  def on_Offset_clicked
    Thread.new {
      alt = @glade.get_widget("Alt_Offset").value_as_int
      az = @glade.get_widget("Az_Offset").value_as_int
      alt_time = (alt.to_f/300.0).abs
      az_time = (az.to_f/300.0).abs

      if alt < 0
	alt_dir = 's'
      else
	alt_dir = 'n'
      end

      if az < 0
	az_dir = 'w'
      else
	az_dir = 'e'
      end

      @mutex.synchronize {
	oldrate = @rate
	@scope.rate('Center')

	if alt != 0
	  @scope.move(alt_dir)
	  sleep(alt_time)
	  @scope.haltall
	end

	if az != 0
	  @scope.move(az_dir)
	  sleep(az_time)
	  @scope.haltall
	end

	@rate = oldrate
      }
    }
  end

  def on_GuideRate_clicked
    Thread.new {
      rate = @glade.get_widget("GuideRate_Spinner").value
      @mutex.synchronize {
	@scope.set_guide_rate(rate)
      }
    }
  end

end

### define the GUI
class LX200_GUI

  Star = Struct.new('Star', :name, :mag, :class, :ra, :dec, :dist)
  COLUMN_HR, COLUMN_NAME, COLUMN_MAG, COLUMN_CLASS, COLUMN_RA, COLUMN_DEC, COLUMN_SECZ, 
    NUM_COLUMNS = *(0..6).to_a
 
  def initialize(serport='/dev/ttyUSB0')
    @lx200 = LX200.new(serport)
    @prev = Hash.new

    @params = ['cat_id', 'rot', 'cat_ra2000', 'cat_dec2000', 'cat_rapm', 
      'cat_decpm', 'pa', 'cat_epoch', 'instazoff', 'insteloff',
      'azoff', 'eloff', 'raoff', 'decoff']

    @glade = GladeXML.new("#{$path}/lx200/lx200.glade") {|handler| method(handler)}

    @glade.get_widget("Title").markup = "<b>LX200 Connected on Port #{serport}</b>"
    @catwindow = @glade.get_widget("MainWindow")
    @status = @glade.get_widget("Status")
    @menubar = @glade.get_widget("menubar1")
 
    @ra_entry = @glade.get_widget("RAEntry")
    @dec_entry = @glade.get_widget("DecEntry")

    @search_entry = @glade.get_widget("Radius")
    @mag_entry = @glade.get_widget("Mag")

    @findhere = @glade.get_widget("FindHere")
    @findtel = @glade.get_widget("FindTel")
    @goto = @glade.get_widget("GoTo")

    @ra = @glade.get_widget("RA")
    @dec = @glade.get_widget("Dec")
    @lst = @glade.get_widget("LST")
    @ha = @glade.get_widget("HA")
    @az = @glade.get_widget("Az")
    @alt = @glade.get_widget("Alt")
    @airmass = @glade.get_widget("Airmass")
    @temp = @glade.get_widget("Temp")

    @model = Gtk::ListStore.new(String, String, Float, String, String, String, Float)
    @tree = @glade.get_widget("OutputTree")
    @tree.model = @model

    # column for HR number
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 1.0
    column = Gtk::TreeViewColumn.new("HR #",
				     renderer,
				     {'text' =>COLUMN_HR})
    column.set_sort_column_id(COLUMN_HR)
    @tree.append_column(column)

    # column for star name
    renderer = Gtk::CellRendererText.new
    column = Gtk::TreeViewColumn.new("Star Name",
				     renderer,
				     {'text' =>COLUMN_NAME})
    column.set_sort_column_id(COLUMN_NAME)
    @tree.append_column(column)

    # column for star mag
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 0.5

    column = Gtk::TreeViewColumn.new("V Mag",
				     renderer,
				     {'text' =>COLUMN_MAG})
    column.set_sort_column_id(COLUMN_MAG)
    column.set_cell_data_func(renderer) do |column, renderer, model, iter|
      renderer.text = sprintf("%.2f", iter[2])
    end

    @tree.append_column(column)

    # column for spectral class
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 0.5
    column = Gtk::TreeViewColumn.new("Spectral Type",
				     renderer,
				     {'text' =>COLUMN_CLASS})
    column.set_sort_column_id(COLUMN_CLASS)
    @tree.append_column(column)

    # column for RA
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 1.0
    column = Gtk::TreeViewColumn.new("      RA\n   (J2000)",
				     renderer,
				     {'text' =>COLUMN_RA})
    column.set_sort_column_id(COLUMN_RA)
    @tree.append_column(column)

    # column for Dec
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 1.0
    column = Gtk::TreeViewColumn.new("       Dec\n    (J2000)",
				     renderer,
				     {'text' =>COLUMN_DEC})
    column.set_sort_column_id(COLUMN_DEC)
    @tree.append_column(column)

    # column for airmass
    renderer = Gtk::CellRendererText.new
    renderer.xalign = 0.5
    column = Gtk::TreeViewColumn.new("Airmass",
				     renderer,
				     {'text' =>COLUMN_SECZ})
    column.set_sort_column_id(COLUMN_SECZ)
    column.set_cell_data_func(renderer) do |column, renderer, model, iter|
      if iter[6]
        renderer.text = sprintf("%.2f", iter[6])
        if iter[6] > 2.0
          renderer.background = "red"
        else
          renderer.background = "white"
        end
      end
    end
    @tree.append_column(column)
    @model.set_sort_column_id(COLUMN_SECZ)

    flush = @lx200.az

    @temp_get = false 

    @paddle = nil
    @is_slewing = false
    @current = Hash.new
    @mutex = Mutex.new
    Thread.abort_on_exception = true

    @hr_catalog = read_catalog
    
    @update = Thread.new {
      loop {
	update_data
        update_catalog
	sleep(1)
      }
    }
      
  end

  # read in HR catalog list used by turbina
  def read_catalog
    file = File.new("/opt/turbina/data/data/star.lst", "r")

    stars = Hash.new
    stars['HR'] = Array.new
    stars['Name'] = Array.new
    stars['RA'] = Array.new
    stars['Dec'] = Array.new
    stars['Vmag'] = Array.new
    stars['BmV'] = Array.new
    stars['SED'] = Array.new
    stars['SpType'] = Array.new

    file.each_line { |line|
      next if line =~ /#/
      stars['HR'].push(line[0..3])
      stars['Name'].push(line[5..11])
      h = "%02d" % line[13..14].to_i
      m = "%02d" % line[16..17].to_i
      s = "%02d" % line[19..20].to_i

      stars['RA'].push("%s:%s:%s" % [h, m, s])

      sign = line[21..22]
      d = "%02d" % line[24..25].to_i
      m = "%02d" % line[27..28].to_i
      s = "%02d" % line[30..31].to_i

      tmp = "%s%s:%s:%s" % [sign, d, m, s]
      stars['Dec'].push(tmp[1..9])

      stars['Vmag'].push(line[33..37].to_f)
      stars['BmV'].push(line[39..43])
      stars['SED'].push(line[45..47])
      stars['SpType'].push(line[49..62])
    }

    return stars
  end

  # return the mutex used to control mount comm
  def mutex
    return @mutex
  end

  # routine to print to statusbar
  def report(text)
    @status.pop(0)
    @status.push(0, text)
  end

  def on_temperature1_activate
    if @glade.get_widget("temperature1").active?
      @temp_get = true
    else
      @temp_get = false
    end
  end

  def on_MainWindow_destroy
    Thread.new {
      @mutex.synchronize {
	flush = @lx200.az
	Gtk.main_quit
      }
    }
  end

  def on_quit1_activate
    Thread.new {
      @mutex.synchronize {
	flush = @lx200.az
	Gtk.main_quit
      }
    }
  end

  def on_stow_activate
    report("Stowing and parking telescope....")
    Thread.new {
      @mutex.synchronize {
        @is_slewing = true
      }
    }
  end

  def on_wake_up_activate
  end

  def on_paddle1_activate
    @paddle = Paddle.new(self, @lx200)
  end

  def on_about1_activate
    puts "write me!"
  end

  def update_data
    outfile = File.new("lx200.log", "a")
    t = "N/A"
    ut = `date -u +'%H:%M:%S'`.chomp

    @mutex.synchronize {
      @is_slewing = @lx200.is_slewing?
      @current['RA'] = @lx200.ra
      @current['LST'] = @lx200.lst
      @current['Dec'] = @lx200.dec
      @current['Az'] = @lx200.az
      @current['Alt'] = @lx200.alt
      if @temp_get
        t = @lx200.temp.to_s
	@current['Temp'] = t + "<sup>o</sup> C"
      else
        t = "N/A"
        @current['Temp'] = "N/A"
      end

      (d, m, s) = @current['Alt'].split(':')
      alt = d.to_f + m.to_f/60.0 + s.to_f/3600.0
      @current['Airmass'] = sprintf("%6.2f", 1.0/Math::cos(Math::PI*(90.0-alt)/180.0))

      (ra_h, ra_m, ra_s) = @current['RA'].split(':')
      ra = ra_h.to_f + ra_m.to_f/60.0 + ra_s.to_f/3600.0
      (lst_h, lst_m, lst_s) = @current['LST'].split(':')
      lst = lst_h.to_f + lst_m.to_f/60.0 + lst_s.to_f/3600.0

      ha = lst - ra
      @current['HA'] = sexagesimal(ha)

      @current.each_key { |key|
        @glade.get_widget("#{key}").markup = @current[key]
      }
    }

    out = sprintf("%s %s %s %s %s %s %s %s %s\n", 
                  ut, 
                  @current['RA'],
                  @current['Dec'],
                  @current['LST'],
                  @current['HA'],
                  @current['Az'],
                  @current['Alt'],
                  @current['Airmass'],
                  t
                  )
    outfile.print(out)
    outfile.close
    outfile = nil
  end

  # this can convert ha,dec to az,el or vice versa.  arguments given in degrees.
  def eqazel(ha, dec)
    lat = Math::PI*hms2deg("-32:22:32")/180.0
    h = Math::PI*ha/180.0
    d = Math::PI*dec/180.0
    sphi = Math::sin(lat)
    cphi = Math::cos(lat)
    sleft = Math::sin(h)
    cleft = Math::cos(h)
    sright = Math::sin(d)
    cright = Math::cos(d)
    az = Math::atan2(-1.0*sleft, -1.0*cleft*sphi + sright*cphi/cright)
    az = (az < 0.0) ? az + 2.0*Math::PI : az
    el = Math::asin(cleft*cright*cphi + sright*sphi)
    if el > 0.0
      airmass = 1.0/Math::cos(Math::PI/2.0 - el)
    else 
      airmass = 50.0
    end
    return az, el, airmass
  end

  def update_catalog
    @mutex.synchronize {
      sel = @tree.selection.selected
      if sel
        hr = sel.get_value(0).to_i
      end
      @model.clear
      (0..@hr_catalog['RA'].size-1).each { |i|
        ra = 15.0*hms2deg(@hr_catalog['RA'][i])
        dec = hms2deg(@hr_catalog['Dec'][i])
        lst = 15.0*hms2deg(@current['LST'])
        ha = lst - ra
        next if dec > 30.0
        az, el, airmass = eqazel(ha, dec)
        next if airmass > 2.5
        iter = @model.append
        iter.set_value(0, @hr_catalog['HR'][i])
        iter.set_value(1, @hr_catalog['Name'][i])
        iter.set_value(2, @hr_catalog['Vmag'][i])
        iter.set_value(3, @hr_catalog['SpType'][i])
        iter.set_value(4, @hr_catalog['RA'][i])
        iter.set_value(5, @hr_catalog['Dec'][i])
        iter.set_value(6, airmass)
        if iter.get_value(0).to_i == hr
          @tree.selection.select_iter(iter)
        end
      }
      @tree.model = @model
    }
  end

  def on_Sync_clicked
    Thread.new {
      @mutex.synchronize {
	obj_ra = sexagesimal(hms2deg(@lx200.obj_ra))
	obj_dec = sexagesimal(hms2deg(@lx200.obj_dec))
	if obj_ra && obj_dec
	  result = @lx200.sync
	  report("Mount Synced to  RA: #{obj_ra}   Dec: #{obj_dec}.")
	else
	  report("No object coordinates in mount memory.")
	end
      }
    }
  end

  def on_GoTo_clicked
    iter = @tree.selection.selected
    if (iter)
      name = iter.get_value(1)
      ra = iter.get_value(4)
      dec = iter.get_value(5)
      report("Moving to: #{name} #{ra} #{dec}")
      Thread.new {
	@mutex.synchronize {
	  @goto.set_sensitive(false)
	  @glade.get_widget("Sync").set_sensitive(false)
	  move_tel(ra, dec, name)
	}
      }
    else
      report("Please select a star.")
    end
  end

  def move_tel(ra, dec, name)
    result = nil
    @mutex.synchronize {
      @lx200.target_ra(ra)
      @lx200.target_dec(dec)
      result = @lx200.slew
      @is_slewing = true
    }
    if result !~ /Slewing/
      report("Problem slewing to #{name}: #{result}.")
    else
      report("Slew OK: #{result}.")
      Thread.new {
	n = 0
	loop {
	  if !@is_slewing
	    report("Move to #{name} successfully completed.")
	    @glade.get_widget("Sync").set_sensitive(true)
	    @goto.set_sensitive(true)
	    break
	  end
	  n = n + 1
	  if n > 90
	    report("Move to #{name} timed out.")
	    @glade.get_widget("Sync").set_sensitive(true)
	    @goto.set_sensitive(true)
	    break
	  end
	  sleep(1)
	}
      }
    end
  end

  def sexagesimal(angle)
    angle = angle.to_f
    if (angle < 0)
      angle = -angle
      sign = "-"
    else
      sign = "+"
    end

    d = angle.to_i
    x = (angle - d.to_f)*60.0
    m = x.to_i
    s = (x - m.to_f)*60.0

    return sprintf("%s%02d:%02d:%02d", sign, d, m, s)
  end

  def hms2deg(string)
    vals = string.split(':')
    return 'bad' if vals.size != 3
    hour = vals[0].to_f
    min  = vals[1].to_f
    sec  = vals[2].to_f
    blah = hour + min/60.0 + sec/3600.0
    if (string =~ /-/ && blah > 0.0)
      blah = blah * -1
    end
    return blah
  end
end

Gtk.init
if ARGV[0]
  LX200_GUI.new(ARGV[0])
else
  LX200_GUI.new('/dev/ttyUSB0')
end
Gtk.main
