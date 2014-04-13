# read in HR catalog list used by turbina
def hr_catalog
  file = File.new("star.lst", "r")

  stars = Hash.new
  star = Hash.new

  file.each_line { |line|
    star = { }
    next if line =~ /#/
    hr = line[0..3].strip
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

def calc_ha(lst, r)
  ha1 = lst - r
  ha2 = lst - (r - 360.0)
  if ha2 > ha1
    ha = ha2
  else
    ha = ha1
  end

  if ha > 360.0
    ha = ha - 360.0
  end

  if ha > 180.0
    ha = ha - 360.0
  end
  return ha
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
  el = 180.0*el/Math::PI
  az = 180.0*az/Math::PI
  return az, el, airmass
end

def best_star(lst)
  lst = 15*hms2deg(lst)
  cat = hr_catalog

  cat.keys.each { |star|

    r = 15*hms2deg(cat[star][:ra])
    d = hms2deg(cat[star][:dec])

    ha = calc_ha(lst, r)

    az, el, airmass = eqazel(ha, d)

    cat[star][:ha] = sexagesimal(ha/15.0)
    cat[star][:az] = sexagesimal(az)
    cat[star][:el] = sexagesimal(el)
    cat[star][:airmass] = airmass

  }

  sort = cat.sort { |a,b|  a[1][:vmag] <=> b[1][:vmag] }

  good = Array.new
  sort.each { |s|
    if s[1][:airmass] < 1.6 && s[1][:vmag] < 2.3 && hms2deg(s[1][:ha]) > 0.5
      good.push(s[0])
    end
  }
  return good[0], good[1]
end

def vis_strip(lst)
  lst = 15*hms2deg(lst)
  cat = hr_catalog

  cat.keys.each { |star|

    r = 15*hms2deg(cat[star][:ra])
    d = hms2deg(cat[star][:dec])

    ha = calc_ha(lst, r)

    az, el, airmass = eqazel(ha, d)

    cat[star][:ha] = sexagesimal(ha/15.0)
    cat[star][:az] = az
    cat[star][:el] = el
    cat[star][:airmass] = airmass

  }

  sort = cat.sort { |a,b|  a[1][:vmag] <=> b[1][:vmag] }

  good = Array.new
  sort.each { |s|
    if s[1][:el] < 65.0 && s[1][:el] > 43.0 
      good.push(s[0])
    end
  }
  return good

end
