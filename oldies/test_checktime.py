import time
from pygto900 import GTO900
import datetime as dt

if 1: #with GTO900() as g:
     #g.set_local_time()
     for i in range(100):
         print dt.datetime.now()#, g.get_local_time()
         time.sleep(10)
