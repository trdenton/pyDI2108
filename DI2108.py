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


  PACKET_SIZE_16=0
  PACKET_SIZE_32=1
  PACKET_SIZE_64=2
  PACKET_SIZE_128=3
  PACKET_SIZE_256=4
  PACKET_SIZE_512=5
  PACKET_SIZE_1024=6
  PACKET_SIZE_2048=7

  PACKET_SIZE_ARG_TO_SIZE=[  16,  32,  64,  128,  256,  512,  1024,  2048  ]

  SCAN_MODE_NORMAL=0
  SCAN_MODE_EXTERNAL=2
  SCAN_MODE_IMMEDIATE=3

  CHANNEL_ANALOG_0=0
  CHANNEL_ANALOG_1=1
  CHANNEL_ANALOG_2=2
  CHANNEL_ANALOG_3=3
  CHANNEL_ANALOG_4=4
  CHANNEL_ANALOG_5=5
  CHANNEL_ANALOG_6=6
  CHANNEL_ANALOG_7=7
  CHANNEL_DIGITAL_IN=8
  CHANNEL_DIGITAL_RATE=9
  CHANNEL_DIGITAL_COUNT=10
  CHANNEL_IGNORE=0xFF
  CHANNEL_DIGITAL_RATE_RANGE_50000HZ=(1<<8)
  CHANNEL_DIGITAL_RATE_RANGE_20000HZ=(2<<8)
  CHANNEL_DIGITAL_RATE_RANGE_10000HZ=(3<<8)
  CHANNEL_DIGITAL_RATE_RANGE_5000HZ=(4<<8)
  CHANNEL_DIGITAL_RATE_RANGE_2000HZ=(5<<8)
  CHANNEL_DIGITAL_RATE_RANGE_1000HZ=(6<<8)
  CHANNEL_DIGITAL_RATE_RANGE_500HZ=(7<<8)
  CHANNEL_DIGITAL_RATE_RANGE_200HZ=(8<<8)
  CHANNEL_DIGITAL_RATE_RANGE_100HZ=(9<<8)
  CHANNEL_DIGITAL_RATE_RANGE_50HZ=(10<<8)
  CHANNEL_DIGITAL_RATE_RANGE_20HZ=(11<<8)
  CHANNEL_DIGITAL_RATE_RANGE_10HZ=(12<<8)

  LED_OFF=0
  LED_BLUE=1
  LED_GREEN=2
  LED_CYAN=3
  LED_RED=4
  LED_MAGENTA=5
  LED_YELLOW=6
  LED_WHITE=7

  '''
  :returns: array of usb devices corresponding to the DI2108
  '''
  @staticmethod
  def _get_devices():
    return map(DI2108,list(usb.core.find(find_all=True,idVendor=DI2108.ID_VENDOR, idProduct=DI2108.ID_PRODUCT)))

  
  @staticmethod
  def list_devices():
    return DI2108._get_devices()


  '''
  Initialize the DI2108
  :param dev: usb.core.Device instance corresponding to the DI2108
  '''
  def __init__(self,dev):
    self.last_reading=None
    self.usb_device=dev
    self.usb_device.reset()
    if(self.usb_device.is_kernel_driver_active(DI2108.INTERFACE_NUM)):
      self.usb_device.detach_kernel_driver(DI2108.INTERFACE_NUM)
    self.set_packet_size(DI2108.PACKET_SIZE_64)

  '''
  Close the device
  '''
  def close(self):
    self.usb_device.reset()
    return self.usb_device.attach_kernel_driver(DI2108.INTERFACE_NUM)

  '''
  Read a command echo from the DI2108
  '''
  def _read_command_response(self):
    size=self.packet_size
    output=bytearray()
    x=self.usb_device.read(DI2108.ENDPOINT_IN,size,timeout=400)
    output.extend(x)
#    while(x[-1]!=0):
#      print "Waiting..."
#      x=self.usb_device.read(DI2108.ENDPOINT_IN,size,timeout=400)
#      output.extend(x)
    return output.decode('ascii')



  '''
  Write to the DI2108
  :param arr: array of ints to write to DI2108
  '''
  def _write(self,arr):
    return self.usb_device.write(DI2108.ENDPOINT_OUT,bytearray(arr))


  '''
  Write to the DI2108
  :param arr: array to write, appends end-of-message
  '''
  #def _write_cmd_bytes(self,arr):
  #  return self._write(arr)  #append carriage return

  def _write_cmd_string(self,string):
    ascii_string = string.encode('ascii')
    self._write(ascii_string)

  def _write_cmd_args(self,args):
    out_string = " ".join(args)
    out_string += "\r"
    self._write_cmd_string(out_string)

  #
  # DATAQ commands
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
    #empirically found that there needs to be a space afterward if arg0 == 0??
    arg=str(arg0)
    if(arg=="0"):
      arg += " "
    self._write_cmd_args(['info',arg]) 
    ret=self._read_command_response()
    ret=ret.split("info %s "%arg)[1]
    return ret.strip()
    

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
    self._write_cmd_args(['ps',str(arg0)+' '])
    ret= self._read_command_response()
    return ret.rstrip()==("ps %s"%arg0)

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
    self._write_cmd_args(['stop '])
    self._read_command_response()
 
  def slist(self,arg0,arg1):
    """Used to configure the scan list.

    parameters:
    arg0 -- offset
    arg1 -- config

    returns an echo
    """
    self._write_cmd_args(['slist',str(arg0),str(arg1)])
    return  self._read_command_response()
 
  def srate(self,arg0):
    """defines a sample rate divisor used to determine scan rate, or the rate at which the DI-
    2108 scans through the items in the scan list that you defined with the slist command

    Sample rate per scan list element (Hz) = 60,000,000 / (srate * dec)

    parameters:
    arg0 -- the srate to set

    returns an echo 
    """
    self._write_cmd_args(['srate',str(arg0)])
    return  self._read_command_response()

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
    arg0=str(arg0)
    arg1=str(arg1)
    arg1+=" "
    self._write_cmd_args(['filter',arg0,arg1])
    return  self._read_command_response()
 
  def dec(self,arg0):
    """sets the number of samples used to calculate the CIC filter

    parameters:
    arg0 -- 1 <= arg0 <= 512 sets the number of values used by the Acquisition Mode defined by the filter
            command.
    """
    self._write_cmd_args(['dec',str(arg0)+' '])
    return  self._read_command_response()

  def ffl(self,arg0):
    """Configure the moving average filter

    parameters:
    arg0 -- the MA factor

    returns an echo
    """
    self._write_cmd_args(['ffl',str(arg0)])
    return  self._read_command_response()

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
    return  self._read_command_response()

  def dout(self,arg0):
    self._write_cmd_args(['dout',str(arg0)])
    return  self._read_command_response()

  def endo(self,arg0):
    """defines configuration on a per port basis, input or switch.

    parameters:
    arg0 -- binary configuration; 0 <= arg0 <= 12710 and maps input/switch configuration to each of seven digital ports. A value
            of one written to a port configures it as a switch. A value of zero configures the port as an
            input. 

    returns an echo
    """
    self._write_cmd_args(['endo',str(arg0)])
    return  self._read_command_response()

  def din(self):
    """returns the state of all ports as a 7-bit value.

    returns din <status>
    """
    self._write_cmd_args(['din'])
    return  self._read_command_response()

  def reset(self):
    """reset the DI-2108 counter
    returns an echo
    """
    self._write_cmd_args(['reset 1'])
    return  self._read_command_response()


  #
  # User interface commands
  #

  def check_connection(self):
    return "DATAQ"==self.info(0)

  def get_device_name(self):
    """returns the device name "2108"
    """
    return self.info(1)

  def get_firmware_revision(self):
    """returns firmware revision, 2 hex bytes
    """
    return self.info(2)

  def get_serial_number(self):
    """returns erial number (left-most 8 digits only; right-most two digits are for internal use)
    """
    return self.info(6)

  def get_sample_rate_divisor(self):
    """returns the sample rate divisor value (60,000,000 for the DI-2108)
    """
    return int(self.info(9))

  def set_packet_size(self,arg):
    """sets the packet size
    arg - one of PACKET_SIZE_16, PACKET_SIZE_32, PACKET_SIZE_64, PACKET_SIZE_128, PACKET_SIZE_256, 
          PACKET_SIZE_512, PACKET_SIZE_1024, PACKET_SIZE_2048
    """
    self.packet_size=DI2108.PACKET_SIZE_ARG_TO_SIZE[arg]
    self.ps(arg)

  def get_packet_size(self):
    """returns the packet size- one of PACKET_SIZE_16, PACKET_SIZE_32, PACKET_SIZE_64, PACKET_SIZE_128, 
        PACKET_SIZE_256, PACKET_SIZE_512, PACKET_SIZE_1024, PACKET_SIZE_2048
    """
    return self.packet_size


  def start_reading(self,arg):
    """Start reading data
    arg -- one of SCAN_MODE_NORMAL, SCAN_MODE_EXTERNAL, SCAN_MODE_IMMEDIATE
    """
    self.scan(arg)

  def stop_reading(self,arg):
    """Stop reading data
    """
    try:
      self.read_data()
    except Exception as e:
      pass
    self.stop()

  def add_channel_to_list(self,pos,ch):
    """Add channel to scan list
    pos -- the position to add ch to  in the scan list (0-11)
    ch -- the channel to use (CHANNEL_ANALOG_0, etc)
    """
    self.slist(ch,pos)

  def read_data(self,timeout=10):
    try:
      x=self.usb_device.read(DI2108.ENDPOINT_IN,self.packet_size,timeout=timeout)
      self.last_reading=x
      return True
    except Exception as e: #data timed out
      return False

  def get_last_data_block(self):
    return self.last_reading

  def get_channel(self,channel_num):
    #split up every 2 bytes
    if self.last_reading != None:
      byte_1 = self.last_reading[channel_num*2]
      byte_2 = self.last_reading[channel_num*2+1]
      return (byte_2<<8)|(byte_1)
    else:
      return None


  def get_analog_channel(self,channel_num):
    data=self.get_channel(channel_num)
    if data != None:
      #signed, 16-bit twos complement
      if (data & (1<<15)) != 0:
        data = data-(1<<16)
      volts = 10.0*data/32768.0
      return volts
    else:
      return None
      

      
    

if __name__=="__main__":
  d= DI2108.list_devices()		

  for x in xrange(1,10):
    print d[0].info(x)
