#!/usr/bin/env python

import os
import re
import ephem
import timdimm
import datetime


def get_stars(site, cat):
    good = []
    el_limit = 25.0 * ephem.pi / 180.0
    az_limit = 180.0 * ephem.pi / 180.0
    for key, star in cat.items():
        if star.az > az_limit and star.alt > el_limit:
            good.append(key)
    good.sort(lambda x, y: cmp(cat[x].dec, cat[y].dec))
    print good
    return good


if __name__ == '__main__':

    now = datetime.datetime.today()
    file = "%4d%02d%02d_west.dat" % (now.year, now.month, now.day)

    salt = timdimm.salt_site()
    cat = timdimm.hr_catalog(salt)
    stars = get_stars(salt, cat)

    for s in stars:
        salt.date = ephem.now()
        star = cat[s]
        star.compute(salt)
        print "Going to HR %s (%s)" % (s, star.name)
        print "RA = %s;  Dec = %s" % (star.ra, star.dec)
        lst = salt.sidereal_time()
        ha = ephem.hours(lst - star.ra)
        print "HA = %s;  Alt = %s;  Az = %s" % (ha, star.alt, star.az)
        os.system("./gto900_hr.rb %s" % s)
        while True:
            res = raw_input('---> ')
            if re.match('[NESW]', res):
                print "Nudge %s" % res.lower()
                os.system("./gto900_nudge.rb %s" % res.lower())
            elif re.match('[nesw]', res):
                print "Tweak %s" % res.lower()
                os.system("./gto900_tweak.rb %s" % res.lower())
            elif re.match('[kK]', res):
                print "Skipping"
                break
            elif re.match('[aA]', res):
                print "Accept"
                os.system("./tpoint_gto.rb %s >> %s" % (s, file))
                break
            elif re.match('[qQxX]', res):
                print "Exiting..."
                os.system("./gto900_park.rb")
                exit()
            else:
                print "\tNESW for big move"
                print "\tnesw for little move"
                print "\tk to skip"
                print "\ta to accept to move on"
                print "\tx or q to exit"
