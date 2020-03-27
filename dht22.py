#!/usr/bin/python3

"""
DHT22 driver
YF Robotics Laboratory (http://www.yfrl.org)
"""

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT


def getDHTSensorData():
  RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 7)
  return (T, RH)


# call main
if __name__ == '__main__':
  print('starting...')
  while True:
     try:
         T, RH = getDHTSensorData()
         print(T, RH)
     except:
         print('exiting.')
         break
