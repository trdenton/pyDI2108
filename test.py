#!/usr/bin/python
import time
from DI2108 import DI2108

ds= DI2108.list_devices()		

#get first device
d = ds[0]


d.reset()

#test info commands
print d.info(0)
print d.info(1)
print d.info(2)
print d.info(6)
print d.info(9)

d.set_packet_size(DI2108.PACKET_SIZE_2048)
d.set_packet_size(DI2108.PACKET_SIZE_1024)
d.set_packet_size(DI2108.PACKET_SIZE_512)
d.set_packet_size(DI2108.PACKET_SIZE_256)
d.set_packet_size(DI2108.PACKET_SIZE_128)
d.set_packet_size(DI2108.PACKET_SIZE_64)
d.set_packet_size(DI2108.PACKET_SIZE_32)
d.set_packet_size(DI2108.PACKET_SIZE_16)

#test LED commands
for x in xrange(0,8):
  d.led(x)
  time.sleep(0.2)


#try reading some data
d.led(DI2108.LED_GREEN)
d.add_channel_to_list(0,DI2108.CHANNEL_ANALOG_0)
d.set_packet_size(DI2108.PACKET_SIZE_16)
raw_input("Hit enter to begin")
d.start(DI2108.SCAN_MODE_IMMEDIATE)

