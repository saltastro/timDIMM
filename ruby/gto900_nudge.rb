#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'

dir = ARGV[0]

s = GTO900.new()

s.clear
s.set_center_rate(10)
s.move(dir)
sleep(1)
s.clear
s.halt(dir)
sleep(1)
s.close
