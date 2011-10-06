#!/usr/bin/env python

import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from pylab import *
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import datetime

def converttime(date, time):
    s="%s %s" % (date,time)
    return datetime.datetime.strptime(s,"%Y%m%d %H%M%S")

def format_time(x, pos=None):
    return dates.num2date(x).strftime('%H')

time = []
flux = []
std = []

flux1 = open("Flux1.dat")
flux2 = open("Flux2.dat")

lines1 = flux1.readlines()
lines2 = flux2.readlines()

for i in range(len(lines1)):
    d1 = lines1[i].split()
    d2 = lines2[i].split()

    ut = converttime(d1[0], d1[1])
    time.append([ut])

    flux.append([float(d1[2])+float(d2[2])])
    std.append([sqrt(float(d1[3])**2 + float(d2[3])**2)])

ut = array(time)
flux1 = array(flux)
std1 = array(std)


fig = figure()
ax = fig.add_subplot(111)
ax.set_ylabel("Flux")
ax.set_xlabel("UT")

ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))

plot_date(ut, flux)

show()