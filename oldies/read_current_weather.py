# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:25:00 2013

@author: jpk

This script returns the current weather information which was written by the 
WeatherPlot script. The average values for the current weather conditions are
returned, as well as warning flags set by the WeatherPlot script. Checks were 
build in to ensure the data received are valid. 
"""

import MySQLdb as ml
import numpy as np
import datetime

def read_current_weather():
    # open a mysql connection
    try:
        conn = ml.connect(host = "db2.suth.saao.ac.za",user = "weatherreader",passwd = "weatherreader",db = "suthweather")
        cursor = conn.cursor()
    # for any connection issue, return a FALSE validity flag
    except ml.Error, e:
        valid = False
        return valid, [0]
  
    # query the current weather table
    cursor.execute("select * from current_weather")
    temp = cursor.fetchall()
    
    # close the mysql connection
    cursor.close()
    conn.close()
    
    # make a recarray from the current weather
    try:    
        cw = np.array(list(temp),dtype=[('datetime','S20'),
                      ('avg_t_min_tdew', 'f4'),('avg_hum', 'f4'),
                        ('avg_cloud', 'f4'),('avg_wind', 'f4'),
                        ('avg_temp', 'f4'),('t_min_tdew_warn', 'i4'),
                        ('hum_warn', 'i4'),('rain_warn', 'i4'),
                        ('cloud_warn', 'i4'),('wind_warn', 'i4'),
                        ('temp_warn', 'i4')])[0]
                        
    # if the retuned tuple is empty, no current weather data is available
    except IndexError:
        valid = False
        return valid, [0]
        
    # check the time stamp validity. All the times are in SAST
    cw_time = datetime.datetime.strptime(cw['datetime'], '%Y-%m-%d %H:%M:%S')
    timediff = datetime.datetime.now() - cw_time # make sure system time is in SAST
    
    # if the current weather info is older than 10min return a FALSE validity 
    # flag
    if timediff.seconds > 600:
        valid = False
        return valid, [0]
    else:
        valid = True
        
    # if all the checks were passed, return the validity flag and 
    # the rec array with the current weather info
    return valid, cw
    
if __name__ == "__main__":
    valid, cw = read_current_weather()
    
    if valid:
        print ""
        print "------------ Current Weather Info ------------"
        print "TimeStamp (SAST)   : ", cw['datetime']
        print "Avg. T - T(dew)    : ", cw['avg_t_min_tdew']
        print "Avg. Humidity      : ", cw['avg_hum']
        print "Avg. Rel. Sky Temp : ", cw['avg_cloud']
        print "Avg. Wind Speed    : ", cw['avg_wind']
        print "Avg. Temp          : ", cw['avg_temp']
        print "------------ Warnings ------------------------"
        print " T - T(dew) Warn.  : ", cw['t_min_tdew_warn'] 
        print " Hum. Warn.        : ", cw['hum_warn']
        print " Sky Con. Warn.    : ", cw['rain_warn']
        print " Cloud Warn.       : ", cw['cloud_warn']
        print " Wind Speed Warn.  : ", cw['wind_warn']
        print " Temp Warn.        : ", cw['temp_warn']
        print ""
        print ""
        print " Warn = 0 --> All clear"
        print " Warn = 1 --> Warning, Close to Closing Limits"
        print " Warn = 2 --> Close Telescope"   
        print ""
        print ""
    else:
        print ""
        print "No current weather information is available, close telescope"
        print ""
    