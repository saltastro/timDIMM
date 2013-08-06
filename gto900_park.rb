#!/usr/bin/env ruby

require 'GTO900'
require 'ast_utils'
require 'timeout'

begin
  timeout(10) {
    s = GTO900.new()

    s.clear
    s.shutdown

    s.close
  }
rescue TimeoutError
  puts "Timeout attempting to park telescope. Power off?"
rescue => why
  puts "Error parking telescope: %s" % why
end
