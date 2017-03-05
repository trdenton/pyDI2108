#!/usr/bin/python
import numpy as np
import time
import csv
from DI2108 import DI2108

class Laser:
  """
  A really simple class that uses one-off measurements from the DI2108 on one analog channel
  """
  def __init__(self,channel_num):
    self.cal_slope=1.0
    self.cal_intercept=0.0
    self.channel_num=channel_num
    self.dataq=None
    self.open()
    self.dataq.add_channel_to_list(0,channel_num)
    self.dataq.led(DI2108.LED_BLUE)
    #minimum sampling rate
    self.dataq.srate(65535)

    #decimation filter size 128
    self.dataq.filter(DI2108.CHANNEL_ANALOG_0,1)
    self.dataq.dec(128)

    self.dataq.set_packet_size(DI2108.PACKET_SIZE_16) 

  def open(self):
    if(self.dataq==None):
      ds=DI2108.list_devices()
      if (len(ds)>0):
        self.dataq=ds[0]

  def volts_to_distance(self,volts):
    return (volts*self.cal_slope)+self.cal_intercept

  def get_reading(self):
    self.dataq.start(DI2108.SCAN_MODE_NORMAL)
    while self.dataq.read_data()==False:
      pass
    self.dataq.stop()
#    dat=self.dataq.get_last_data_block()
#    print "Got last data block size %d"%len(dat)

    volts = self.dataq.get_analog_channel(self.channel_num)
    mm = self.volts_to_distance(volts)
    print "volts: %f distance: %f"%(volts,mm)
    return mm

  def calibrate(self,filename):
    with open(filename,'wb') as csvfile:
      writer=csv.writer(csvfile,delimiter=',')
      try:
        while True:
          dist=raw_input("Enter distance in mm.  Hit enter to take reading, Ctrl-C to stop> ")
          dist_int = int(dist)
          reading = self.get_reading()
          writer.writerow([dist_int,reading])
      except KeyboardInterrupt as ki:
        print "done calibrating"
      

  def read_calibration(self,filename):
    with open(filename,'rb') as csvfile:
      reader=csv.reader(csvfile,delimiter=',')
      data = [row for row in reader]
      xd = [float(row[1]) for row in data]
      yd = [float(row[0]) for row in data]
      par = np.polyfit(xd, yd, 1, full=True)
      self.cal_slope=par[0][0]
      self.cal_intercept=par[0][1] 
      print "slope %f intercept %f"%(self.cal_slope,self.cal_intercept)
  

if __name__=="__main__":
  l = Laser(DI2108.CHANNEL_ANALOG_0)
  #l.calibrate('test.csv')
  #l.read_calibration("test.csv")
  print l.get_reading()
  
