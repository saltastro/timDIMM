#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

scope = GTO900.new('localhost', 7001)

lines = IO.readlines("init_cen_all")

tol = 85.0

scope.set_center_rate(5)

side = scope.pier?

puts "Scope is #{side} of the pier.\n"

minx = 1000.0
maxx = 0.0
miny = 1000.0
maxy = 0.0

lines.each { |line|
  x, y = line.split(' ')
  x = x.to_f
  y = y.to_f
  if x > maxx
    maxx = x
  end
  if x < minx
    minx = x
  end
  if y > maxy
    maxy = y
  end
  if y < miny
    miny = y
  end
}

if maxx > 320-tol
  print "Move South."
  scope.move('s')
end
if minx < tol
  print "Move North."
  scope.move('n')
end
if miny < tol
  if side == 'West'
    print "Move West."
    scope.move('w')
  else
    print "Move East."
    scope.move('e')
  end
end
if maxy > 240-tol
  if side == 'West'
    print "Move East."
    scope.move('e')
  else
    print "Move West."
    scope.move('w')
  end
end

sleep(1)
scope.haltall
sleep(1)
scope.close

