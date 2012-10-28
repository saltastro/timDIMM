#!/usr/bin/env python

import xml
import sys
import html5lib
import urllib2
import xml.dom.minidom
from numpy import median, array
from xml_icd import *

from html5lib import treebuilders


def salt():
    wx = {}
    try:
        tcs = parseICD("http://sgs.salt/xml/salt-tcs-icd.xml")
        time = tcs['tcs xml time info']
        bms = tcs['bms external conditions']
        temps = array(bms['Temperatures'])

        # get temps and take median of the BMS output of 7 values
        wx["Temp"] = median(temps)

        # get time
        wx["SAST"] = time["SAST"].split()[1]
        wx["Date"] = time["SAST"].split()[0]

        # set up other values of interest
        wx["Air Pressure"] = bms["Air pressure"] * 10.0
        wx["Dewpoint"] = bms["Dewpoint"]
        wx["RH"] = bms["Rel Humidity"]
        wx["Wind Speed (30m)"] = bms["Wind mag 30m"] * 3.6
        wx["Wind Speed"] = bms["Wind mag 10m"] * 3.6
        wx["Wind Dir (30m)"] = bms["Wind dir 30m"]
        wx["Wind Dir"] = bms["Wind dir 10m"]
        wx["T - DP"] = wx["Temp"] - bms["Dewpoint"]
        wx["Raining"] = bms["Rain detected"]
        return wx
    except:
        return False


def wasp():
    wx = {}
    try:
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        doc = p.parse(urllib2.urlopen("http://swaspgateway.suth/",
                                      timeout=1).read())
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
    kan11 = p.parse(urllib2.urlopen("http://sg1.suth/tmp/kan11.htm",
                                    timeout=1).read())
    kan16 = p.parse(urllib2.urlopen("http://sg1.suth/tmp/kan16.htm",
                                    timeout=1).read())
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
    wx["Wind Speed"] = float(kan16_tds[14].firstChild.nodeValue) * 3.6
    return wx


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: weather.py <salt|wasp|grav>"
    else:
        wx = eval("%s()" % sys.argv[1].lower())
        if wx:
            for k, v in sorted(wx.items()):
                print "%20s : \t %s" % (k, v)
        else:
            print "No information received."
