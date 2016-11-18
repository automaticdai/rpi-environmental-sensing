#!/usr/bin/python3
import io, fcntl
I2C_SLAVE = 0x0703

class i2c(object):
   def __init__(self, slave_addr, bus_index):
      self.fr = io.open("/dev/i2c-" + str(bus_index), "rb", buffering = 0)
      self.fw = io.open("/dev/i2c-" + str(bus_index), "wb", buffering = 0)
      # set device address
      fcntl.ioctl(self.fr, I2C_SLAVE, slave_addr)
      fcntl.ioctl(self.fw, I2C_SLAVE, slave_addr)

   def write(self, bytes):
      self.fw.write(bytes)

   def read(self, bytes):
      return self.fr.read(bytes)

   def close(self):
      self.fw.close()
      self.fr.close()
