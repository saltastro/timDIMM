#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

dir = ARGV[0]

s = GTO900.new('massdimm', 7001)

s.clear
s.set_center_rate(7)
s.move(dir)
sleep(1)
s.clear
s.halt(dir)
s.close
sleep(2)
