#!/usr/bin/env python

import xml
import sys
import html5lib
import urllib2
import xml.dom.minidom

from html5lib import treebuilders

def salt():
    wx = {}
    dbl = {}
    st = {}
    bol = {}
    try:
        url = "http://sgs.salt/xml/salt-tcs-icd.xml"
        doc = xml.dom.minidom.parse(urllib2.urlopen(url, timeout=1))
        doubles = doc.getElementsByTagName("DBL")
        strings = doc.getElementsByTagName("String")
        bools = doc.getElementsByTagName("Boolean")
        arrays = doc.getElementsByTagName("Array")
        temps = arrays[0].getElementsByTagName("DBL")
        temp = 0
        n = 0
        for t in temps:
            val = float(t.getElementsByTagName("Val")[0].firstChild.nodeValue)
            temp = temp + val
            n = n + 1
        temp = temp/n
        wx["Temp"] = temp
        for d in doubles:
            key = d.getElementsByTagName("Name")[0].firstChild.nodeValue
            val = float(d.getElementsByTagName("Val")[0].firstChild.nodeValue)
            dbl[key] = val
        for s in strings:
            key = s.getElementsByTagName("Name")[0].firstChild.nodeValue
            if s.getElementsByTagName("Val")[0].firstChild:
                val = s.getElementsByTagName("Val")[0].firstChild.nodeValue
                st[key] = val
        for b in bools:
            key = b.getElementsByTagName("Name")[0].firstChild.nodeValue
            val = int(b.getElementsByTagName("Val")[0].firstChild.nodeValue)
            if val == 0:
                bol[key] = False
            else:
                bol[key] = True

        wx["SAST"] = st["SAST"].split()[1]
        wx["Date"] = st["SAST"].split()[0]
        wx["Air Pressure"] = dbl["Air pressure"]*10.0
        wx["Dewpoint"] = dbl["Dewpoint"]
        wx["RH"] = dbl["Rel Humidity"]
        wx["Wind Speed (30m)"] = dbl["Wind mag 30m"]*3.6
        wx["Wind Speed"] = dbl["Wind mag 10m"]*3.6
        wx["Wind Dir (30m)"] = dbl["Wind dir 30m"]
        wx["Wind Dir"] = dbl["Wind dir 10m"]
        wx["T - DP"] = temp - dbl["Dewpoint"]
        wx["Raining"] = bol["Rain detected"]
        return wx
    except:
        return False
        
def wasp():
    wx = {}
    try:
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        doc = p.parse(urllib2.urlopen("http://swaspgateway.suth/", timeout=1).read())
        t = doc.getElementsByTagName("table")[0]
        tds = t.getElementsByTagName("td")
        wx["Temp"] = float(tds[7].firstChild.nodeValue)
        if tds[10].firstChild.nodeValue == "RAIN":
            wx["Sky"] = "Rain"
            wx["Sky Temp"] = wx["Temp"]
        else:
            sky, stemp = tds[10].firstChild.nodeValue.split('(')
            stemp = stemp[0:-1]
            wx["Sky"] = sky
            wx["Sky Temp"] = stemp
        wx["T - DP"] = float(tds[9].firstChild.nodeValue)
        wx["RH"] = float(tds[8].firstChild.nodeValue)
        tds[6].normalize()
        wx["Wind Dir"] = tds[6].firstChild.nodeValue[1:]
        wx["Wind Speed"] = float(tds[5].firstChild.nodeValue)
        rain = tds[4].firstChild.nodeValue
        if rain == "DRY":
            wx["Raining"] = False
        else:
            wx["Raining"] = True
        wx["UT"] = tds[3].firstChild.nodeValue.strip()
        tds[31].normalize()
        wx["Status"] = tds[31].firstChild.nodeValue.strip()
        return wx
    except:
        return False

def grav():
    wx = {}
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    kan11 = p.parse(urllib2.urlopen("http://sg1.suth/tmp/kan11.htm", timeout=1).read())
    kan16 = p.parse(urllib2.urlopen("http://sg1.suth/tmp/kan16.htm", timeout=1).read())
    kan11_tds = kan11.getElementsByTagName("td")
    kan16_tds = kan16.getElementsByTagName("td")
    wx["Date"], wx["UT"] = kan11_tds[12].firstChild.nodeValue.split()
    kan11_tds[14].normalize()
    kan11_tds[15].normalize()
    wx["Temp"] = float(kan11_tds[14].firstChild.nodeValue)
    wx["RH"] = float(kan11_tds[15].firstChild.nodeValue)
    kan16_tds[13].normalize()
    kan16_tds[14].normalize()
    wx["Wind Dir"] = int(kan16_tds[13].firstChild.nodeValue)
    wx["Wind Speed"] = float(kan16_tds[14].firstChild.nodeValue)*3.6
    return wx
    
if __name__=='__main__':
    if len(sys.argv) == 1:
        print "Usage: weather.py <salt|wasp|grav>"
    else:
        wx = eval("%s()" % sys.argv[1].lower())
        if wx:
            for k,v in sorted(wx.items()):
                print "%20s : \t %s" % (k,v)
        else:
            print "No information received."
        


