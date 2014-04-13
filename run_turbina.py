#!/usr/bin/env python

import os
import time

def run_turbina():
    """Check to see if turbina is ready.   If so, measure a background and 
       begin running measurements with turbina
    """
 
    status = os.popen('./turbina.rb status').read()

    if status == 'READY':
        time.sleep(3)
        os.system("./pygto900.py nudge s")
        time.sleep(3)
        os.system("./pygto900.py nudge w")
        time.sleep(3)
        os.system('./turbina.rb background')
        sleep(5)
        system("./goto_hr.py")
        sleep(5)
        os.system('./turbina.rb run')



if __name__=='__main__':
   run_turbina()
