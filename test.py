#!/usr/bin/python
import time
from DI2108 import DI2108

ds= DI2108.listDevices()		

#get first device
d = ds[0]


d.reset()

#test info commands
print d.info(0)
print d.info(1)
print d.info(2)
print d.info(6)
print d.info(9)

#test LED commands
for x in xrange(0,8):
  d.led(x)
  time.sleep(0.2)
