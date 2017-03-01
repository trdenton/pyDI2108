#!/usr/bin/python
import usb
import time

'''
Python class for reading DI2108 sensor from porcupine labs
'''

class DI2108(object):

  '''
  usb details
  '''
  ID_VENDOR=0x0683
  ID_PRODUCT=0x2108
  INTERFACE_NUM=0
  ENDPOINT_IN=0x81
  ENDPOINT_OUT=0x01

  '''
  :returns: array of usb devices corresponding to the DI2108 from porcupine labs
  '''
  @staticmethod
  def _getDevices():
    return map(DI2108,list(usb.core.find(find_all=True,idVendor=DI2108.ID_VENDOR, idProduct=DI2108.ID_PRODUCT)))

  
  @staticmethod
  def listDevices():
    return DI2108._getDevices()


  '''
  Initialize the DI2108
  :param dev: usb.core.Device instance corresponding to the DI2108
  '''
  def __init__(self,dev):
    self.usbDevice=dev
    self.usbDevice.reset()
    if(self.usbDevice.is_kernel_driver_active(DI2108.INTERFACE_NUM)):
      self.usbDevice.detach_kernel_driver(DI2108.INTERFACE_NUM)

  '''
  Close the device
  '''
  def close(self):
    self.usbDevice.reset()
    return self.usbDevice.attach_kernel_driver(DI2108.INTERFACE_NUM)

  '''
  Read a byte from the DI2108
  '''
  def _read(self):
    size=16
    output=bytearray()
    x=self.usbDevice.read(DI2108.ENDPOINT_IN,size,timeout=100)
    output.extend(x)
    while(x[-1]!=0):
      x=self.usbDevice.read(DI2108.ENDPOINT_IN,size,timeout=100)
      output.extend(x)
    return output.decode('ascii')



  '''
  Write to the DI2108
  :param arr: array of ints to write to DI2108
  '''
  def _write(self,arr):
    return self.usbDevice.write(DI2108.ENDPOINT_OUT,bytearray(arr))


  '''
  Write to the DI2108
  :param arr: array to write, appends end-of-message
  '''
  def _write_cmd_bytes(self,arr):
    return self._write(arr.append(bytearray([b'0x0D'])))  #append carriage return

  def _write_cmd_string(self,string):
    ascii_string = string.encode('ascii')
    self._write(ascii_string)

  def _write_cmd_args(self,args):
    out_string = " ".join(args) + "\r"
    self._write_cmd_string(out_string)

  def info(self,arg0):
    self._write_cmd_args(['info',str(arg0)]) 
    return self._read()
  
   
 
if __name__=="__main__":
  d= DI2108.listDevices() 		
  print d[0].info(1)
