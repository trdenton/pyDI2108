#!/usr/bin/python
import time
from DI2108 import DI2108

class Laser:
  """
  A really simple class that uses one-off measurements from the DI2108 on one analog channel
  """
  def __init__(self,channel_num):
    self.channel_num=channel_num
    self.dataq=None
    self.open()
    self.dataq.add_channel_to_list(0,channel_num)
    self.dataq.led(DI2108.LED_BLUE)
    self.dataq.set_packet_size(DI2108.PACKET_SIZE_16)

  def open(self):
    if(self.dataq==None):
      ds=DI2108.list_devices()
      if (len(ds)>0):
        self.dataq=ds[0]

  def volts_to_distance(self,volts):
    #TODO implement whatever translation function
    return volts

  def get_reading(self):
    self.dataq.start(DI2108.SCAN_MODE_IMMEDIATE)
    while self.dataq.read_data()==False:
      pass

    volts = self.dataq.get_analog_channel(self.channel_num)
    return self.volts_to_distance(volts)
  

if __name__=="__main__":
  l = Laser(DI2108.CHANNEL_ANALOG_0)
  try:
    while True:
      print "%f"%l.get_reading()
      time.sleep(0.5)
  except KeyboardInterrupt as e:
    print "see ya!"
