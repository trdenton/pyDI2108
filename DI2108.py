#!/usr/bin/python
import usb
import time


'''
Python class for reading DI2108 data acquisition unit
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
  :returns: array of usb devices corresponding to the DI2108
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
    size=128
    output=bytearray()
    x=self.usbDevice.read(DI2108.ENDPOINT_IN,size,timeout=400)
    output.extend(x)
    while(x[-1]!=0):
      x=self.usbDevice.read(DI2108.ENDPOINT_IN,size,timeout=400)
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
    return self._write(arr)  #append carriage return

  def _write_cmd_string(self,string):
    ascii_string = string.encode('ascii')
    self._write(ascii_string)

  def _write_cmd_args(self,args):
    out_string = " ".join(args) + "\r"
    self._write_cmd_string(out_string)

  #
  # User commands
  #
  #

  def info(self,arg0):
    """Get info about the DI2108.

    arguments:
    arg0 -- an integer specifying data to retrieve:
      0 - returns "DATAQ"
      1 - Returns device name: "2108"
      2 - Returns firmware revision, 2 hex bytes (e.g. 6516 = 10110 for firmware revision 1.01)
      3 - Proprietary internal use for initial system verification
      4 - Proprietary internal use for initial system verification
      5 - Proprietary internal use for initial system verification
      6 - info 6 Returns the DI-2108's serial number (left-most 8 digits only; right-most two digital are for internal use)
      7 - Proprietary internal use for initial system verification
      8 - Proprietary internal use for initial system verification
      9 - Returns the sample rate divisor value of 60,000,000 for the DI-2108 (see the srate command for details)

    returns an echo
    """
    self._write_cmd_args(['info',str(arg0)]) 
    return self._read()

  def ps(self,arg0):
    """Set packet size

    arguments:
    arg0 -- an integer specifying packet size:
      0 - Make packet size 16 bytes
      1 - Make packet size 32 bytes
      2 - Make packet size 64 bytes
      3 - Make packet size 128 bytes
      4 - Make packet size 256 bytes
      5 - Make packet size 512 bytes
      6 - Make packet size 1024 bytes
      7 - Make packet size 2048 bytes

    returns an echo
    """
    self._write_cmd_args(['ps',str(arg0)])
    return self._read()

  def start(self,arg0):
    """Initiates scanning (reading inputs)

    arguments:
    arg0 -- bleh
      0 - Normal scanning: The instrument begins scanning the channels enabled in its scan list through the slist command at a rate defined by the srate command.
      1 - Reserved for future use. 
      2 - Scan using an external clock or trigger: The instrument begins scanning the channels enabled in its scan list by
          the slist command at a rate defined by clock transitions applied to its "Ext Trig" input of D6. This scan method
          allows data to be acquired synchronously with external events.
      3 - Immediate scan: The instrument reports the results of a single scan of all channels enabled in its scan list at a
          burst rate of 1 kHz per channel. Analog channels are reported at fixed 16-bit resolution. 

    returns nothing.
    """
    self._write_cmd_args(['start',str(arg0)])
    return  #never echoes

  def stop(self):
    """Terminates scanning.
    returns an echo
    """
    self._write_cmd_args(['stop'])
    return  self._read()
 
  def slist(self,arg0,arg1):
    """Used to configure the scan list.

    parameters:
    arg0 -- offset
    arg1 -- config

    returns an echo
    """
    self._write_cmd_args(['slist',str(arg0),str(arg1)])
    return  self._read()
 
  def srate(self,arg0):
    """defines a sample rate divisor used to determine scan rate, or the rate at which the DI-
    2108 scans through the items in the scan list that you defined with the slist command

    Sample rate per scan list element (Hz) = 60,000,000 / (srate * dec)

    parameters:
    arg0 -- the srate to set

    returns an echo 
    """
    self._write_cmd_args(['srate',str(arg0)])
    return  self._read()

  def filter(self,arg0,arg1):
    """ Changes the acquisition mode for an analog channel.

    parameters:
    arg0 -- analog channel number
    arg1 -- acquisition mode:
      0 - Last Point
      1 - CIC filter
      2 - Maximum
      3 - Minimum

    returns an echo 
    """
    self._write_cmd_args(['filter',str(arg0),str(arg1)])
    return  self._read()
 
  def dec(self,arg0):
    """sets the number of samples used to calculate the CIC filter

    parameters:
    arg0 -- 1 <= arg0 <= 512 sets the number of values used by the Acquisition Mode defined by the filter
            command.
    """
    self._write_cmd_args(['dec',str(arg0)])
    return  self._read()

  def ffl(self,arg0):
    """Configure the moving average filter

    parameters:
    arg0 -- the MA factor

    returns an echo
    """
    self._write_cmd_args(['ffl',str(arg0)])
    return  self._read()

  def led(self,arg0):
    """Turn on the LED

    parameters:
    arg0 -- the LED color:
      0 - black
      1 - blue
      2 - green
      3 - cyan
      4 - red
      5 - magenta
      6 - yellow
      7 - white

    returns an echo
    """
    self._write_cmd_args(['led',str(arg0)])
    return  self._read()

  def dout(self,arg0):
    self._write_cmd_args(['dout',str(arg0)])
    return  self._read()

  def endo(self,arg0):
    """defines configuration on a per port basis, input or switch.

    parameters:
    arg0 -- binary configuration; 0 <= arg0 <= 12710 and maps input/switch configuration to each of seven digital ports. A value
            of one written to a port configures it as a switch. A value of zero configures the port as an
            input. 

    returns an echo
    """
    self._write_cmd_args(['endo',str(arg0)])
    return  self._read()

  def din(self):
    """returns the state of all ports as a 7-bit value.

    returns din <status>
    """
    self._write_cmd_args(['din'])
    return  self._read()

  def reset(self):
    """reset the DI-2108 counter
    returns an echo
    """
    self._write_cmd_args(['reset 1'])
    return  self._read()


if __name__=="__main__":
  d= DI2108.listDevices()		

  for x in xrange(1,10):
    print d[0].info(x)
