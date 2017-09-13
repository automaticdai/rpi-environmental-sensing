"""
dht22.py
Temperature/Humidity monitor using Raspberry Pi and DHT22.
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
