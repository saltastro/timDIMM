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

