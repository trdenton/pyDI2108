#!/usr/bin/python
import time
from DI2108 import DI2108

ds= DI2108.listDevices()		

#get first device
d = ds[0]

#can we change LED colors?

d.reset()
print d.info(1)

for x in xrange(0,8):
  d.led(x)
  time.sleep(1)
