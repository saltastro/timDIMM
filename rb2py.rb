#!/usr/bin/env ruby

#Ruby to python converter
#Author: olamide bakre


RB_FILE = "ast_utils.rb" #Filename of ruby script
OUT_PUT = "python_test_code.py" #Filename of python script

def get_tabs(tab_count)
  return "" if(tab_count < 0)
  return "\t" * tab_count
end

def convert_keyword(text)
  text.gsub!("false","False")
	text.gsub!("true","True")
	text.gsub!("@","self.")
	text.gsub!("nil","None")
	text.gsub!("||","or")
	text.gsub!("&&","and")
	text.gsub!("next","continue")
  text.gsub!(".new(","(")
  text.gsub!("$", "")
  text.gsub!("elsif", "elif")
end


ruby_script = IO.readlines(RB_FILE)
out_script = []
tab_count = 0
i = 0
while(i < ruby_script.size)
  text = ruby_script[i]
  if(text =~ /class\s+([^<\r\n\s]+)\s*(?:<)?\s*(.*)/)
    tab_count = 0
    text.scan(/class\s+([^<\r\n\s]+)\s*(?:<)?\s*(.*)/)
    out_script << sprintf("class %s(%s):", $1, ($2 == "" ? "object" : $2))
    tab_count += 1
  elsif(text =~ /def\s+([^\s(]+)\s*(?:\()?\s*([^)]*)/)
    #text.scan(/def\s+([\w\d_?=!]+)\s*(?:\()?([\w\d_?=!])?(?:\))?/)
    text.scan(/def\s+([^\s(]+)\s*(?:\()?\s*([^)]*)/)
    out_script << sprintf("%sdef %s(self%s%s):",  
        get_tabs(tab_count), ($1 == "initialize" ? "__init__" : $1), ($2 != "" ? ", " : ""), $2)
    tab_count += 1
  elsif(text =~ /(end)$/)
    tab_count -= 1
    out_script << ""
  elsif(text =~ /for\s(.+)\sin\s(.+)/)
    if(text =~ /(.+)(\.\.|\.\.\.)(.+)/)
      text.scan(/for\s(.+)\sin\s(.+)(\.\.|\.\.\.)(.+)/)
      out_script << sprintf("%sfor %s in xrange(%s,%s%s):",
        get_tabs(tab_count), $1, $2, $4, ($3 == ".." ? " + 1" : ""))
    else
      text.scan(/for\s+(.+)\s+in\s+(.+)/)
      out_script << sprintf("%sfor %s in %s:", 
        get_tabs(tab_count), $1, $2)
    end
    tab_count += 1  
  elsif(text =~ /[^\s\t](.+)\s+if(.+)/)
    text.scan(/[^\s\t](.+)\s+if(.+)/)
    out_script << sprintf("%sif%s: %s", get_tabs(tab_count), $2, $1)
  elsif(text =~ /elsif|else/)
    tab_count -= 1
    unless (text =~ /else/)
      text.scan(/(elsif)(.+)/)
      out_script << sprintf("%s%s%s:", get_tabs(tab_count), $1, $2)
    else
      out_script << sprintf("%selse:", get_tabs(tab_count))
    end
    tab_count += 1
  elsif(text =~ /while|if/)
    old_text = text.to_s
    prev_text = ruby_script[i - 1]
    prev_text = convert_keyword(prev_text) if(prev_text != nil)
    prev_text = "" if(prev_text == nil)
    if(prev_text =~ /if|while|for/)
      unless (prev_text =~ /[^\s\t](.+)\s+if\((.+)\)/)
        tab_count += 1 
      end
    end
    text.scan(/(while|if)(.+)/)
    out_script << sprintf("%s%s%s:", get_tabs(tab_count), $1, $2)
    old_tab_count = tab_count
    tab_count += 1
    i += 1
    while(true)
      break if(i >= ruby_script.size)
      text = ruby_script[i]
      prev_text = ruby_script[i - 1]
      prev_text = "" if(prev_text == nil)
      if(text =~ /for\s+(.+)\s+in\s+(.+)/)
        if(text =~ /(.+)(\.\.|\.\.\.)(.+)/)
          text.scan(/for\s+(.+)\s+in\s+(.+)(\.\.|\.\.\.)(.+)/)
          out_script << sprintf("%sfor %s in xrange(%s,%s%s):",
            get_tabs(tab_count), $1, $2, $4, ($3 == ".." ? "+ 1" : ""))
        else
          text.scan(/for\s+(.+)\s+in\s+(.+)/)
          out_script << sprintf("%sfor %s in %s:", 
            get_tabs(tab_count), $1, $2)
        end
        tab_count += 1
        break        
      elsif(text =~ /(end)$/)
        tab_count -= 1
        out_script << ""
      elsif(text =~ /[^\s\t](.+)\s+if(.+)/)
        text.scan(/[^\s\t](.+)\s+if(.+)/)
        out_script << sprintf("%sif%s: %s", get_tabs(tab_count), $2, $1)
      elsif(text =~ /if|while|elsif|else/)
        unless (text =~ /elsif|else/)
          tab_count += 1 if(text =~ /if|while/)
        end
        if(old_text != nil && text =~/if|while|for/)
          unless(text =~ /elsif/)
            tab_count -= 1
            old_text = nil
          end
        end
        tab_count -= 1 if(text =~ /elsif|else/)
        unless (text =~ /else/)
          text.scan(/(while|if|elsif)(.+)/)
          out_script << sprintf("%s%s%s:", get_tabs(tab_count), $1, $2)
        else
          out_script << sprintf("%selse:", get_tabs(tab_count))
        end
        tab_count += 1
      else
        if(text =~ /\$(.+)\s*=/)
          text.scan(/\$(.+)\s*=/)
          out_script << sprintf("%sglobal %s", get_tabs(tab_count), $1)
        end
        text.gsub!("$","")
        text.scan(/(\s*)(\t*)(.+)/)
        out_script << sprintf("%s%s", get_tabs(tab_count), $3)
      end
      #tab_count -= 1
      break if(tab_count == old_tab_count)
      i += 1
    end
  else
    if(text =~ /\$(.+)\s*=/)
      text.scan(/\$(.+)\s*=/)
      out_script << sprintf("%sglobal %s", get_tabs(tab_count), $1)
    end
    text.gsub!("$","")
    text.scan(/(\s*)(\t*)(.+)/)
    out_script << sprintf("%s%s", get_tabs(tab_count), $3) 
  end
  i += 1
end
file = File.new(OUT_PUT, "w")
for text in out_script
  next if(text == "")
  convert_keyword(text)
  #print text, "\n"
	file.write(text + (text.include?("\n") ? "" : "\n"))
end
file.close()
