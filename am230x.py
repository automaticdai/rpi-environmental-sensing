"""
dht22.py
Temperature/Humidity monitor using Raspberry Pi and DHT22.
Data is displayed at thingspeak.com
Original author: Mahesh Venkitachalam at electronut.in
Modified by Adam Garbo on December 1, 2016
"""
import sys
import RPi.GPIO as GPIO
import Adafruit_DHT

def getAMSensorData():
  RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 7)
  return (T, RH)

def test():
  print('starting...')
  while True:
     try:
         T, RH = getAMSensorData()
         print(T, RH)
     except:
         print('exiting.')
         break


# call main
if __name__ == '__main__':
  test()
