# read in HR catalog list used by turbina
def hr_catalog
  file = File.new("/Users/timdimm/MASSDIMM/star.lst", "r")

  stars = Hash.new
  star = Hash.new

  file.each_line { |line|
    star = { }
    next if line =~ /#/
    hr = line[0..3]
    name = line[5..11]
    h = "%02d" % line[13..14].to_i
    m = "%02d" % line[16..17].to_i
    s = "%02d" % line[19..20].to_i
    
    ra = "%s:%s:%s" % [h, m, s]

    sign = line[21..22]
    d = "%02d" % line[24..25].to_i
    m = "%02d" % line[27..28].to_i
    s = "%02d" % line[30..31].to_i

    tmp = "%s%s:%s:%s" % [sign, d, m, s]
    dec = tmp[1..9]
    
    vmag = line[33..37].to_f
    bmv = line[39..43].to_f
    sed = line[45..47]
    sptype = line[49..62]

    star = { :name => name, :ra => ra, :dec => dec, :vmag => vmag }
    stars[hr] = star
  }
  return stars
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
     hour = vals[0].to_f.abs
     min  = vals[1].to_f
     sec  = vals[2].to_f
     blah = hour + min/60.0 + sec/3600.0
     if (string =~ /-/ && blah > 0.0)
       blah = blah * -1
     end
     return blah
end

