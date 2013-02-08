#!/usr/bin/env python

import os
import re
import ephem
import timdimm
import datetime
import NexStar
import time


def run(program, *args):
    pid = os.fork()
    if not pid:
        os.execvp(program, (program,) + args)
    return pid


def get_stars(cat):
    good = []
    el_limit = 25.0 * ephem.pi / 180.0
    az_limit = 1.0 * ephem.pi / 180.0
    for key, star in cat.items():
        if star.az > az_limit and star.alt > el_limit:
            good.append(key)
    good.sort(lambda x, y: cmp(cat[x].az, cat[y].az))
    print good
    return good


def floatify(a):
    return map(lambda x: float(x), a)

dirs = {'U': 'Up',
        'D': 'Down',
        'L': 'Left',
        'R': 'Right'}

if __name__ == '__main__':
    tel = NexStar.NexStar()
    pid = run("./video_feed")
    print "Video PID: %d" % pid
    now = datetime.datetime.today()
    outfile = "%4d%02d%02d_esss.dat" % (now.year, now.month, now.day)
    fp = open(outfile, 'a')

    site = tel.site()
    cat = timdimm.hr_catalog(site)
    stars = get_stars(cat)

    for s in stars:
        site.date = ephem.now()
        star = cat[s]
        star.compute(site)
        print "Going to HR %s (%s)" % (s, star.name)
        print "RA = %s;  Dec = %s" % (star.ra, star.dec)
        lst = salt.sidereal_time()
        ha = ephem.hours(lst - star.ra)
        print "HA = %s;  Alt = %s;  Az = %s" % (ha, star.alt, star.az)
        tel.goto_object(star)
        while True:
            res = raw_input('---> ')
            if re.match('[UDLW]', res):
                print "Nudge %s" % dirs[res.upper()]
                tel.nudge(dirs[res.upper()])
            elif re.match('[udlr]', res):
                print "Tweak %s" % dirs[res.upper()]
                tel.tweak(dirs[res.upper()])
            elif re.match('[kK]', res):
                print "Skipping"
                break
            elif re.match('[aA]', res):
                print "Accept"
                site.date = ephem.now()
                star.compute(site)
                ra = floatify(str(star.ra).split(':'))
                dec = floatify(str(star.dec).split(':'))
                lst = floatify(str(site.sidereal_time()).split(':'))
                lst_min = lst[1] + lst[2]/60.0
                (tel_ra, tel_dec) = tel.get_radec()
                t_ra = floatify(str(tel_ra).split(':'))
                t_dec = floatify(str(tel_dec).split(':'))
                out_str = "%02d %02d %02d %+03d %02d %02d %02d %02d %02d %+03d %02d %02d %02d %.4f\n" %
                (ra[0], ra[1], ra[2], dec[0], dec[1], dec[2],
                 t_ra[0], t_ra[1], t_ra[2], t_dec[0], t_dec[1], t_dec[2],
                 lst[0], lst_min)
                fp.write(out_str)
                break
            elif re.match('[qQxX]', res):
                print "Exiting..."
                os.system("kill -9 %d" % pid)
                fp.close()
                exit()
            else:
                print "\tNESW for big move"
                print "\tnesw for little move"
                print "\tk to skip"
                print "\ta to accept to move on"
                print "\tx or q to exit"

    os.system("kill -9 %d" % pid)
    fp.close()
