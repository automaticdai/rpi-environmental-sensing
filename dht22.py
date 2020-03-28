#!/usr/bin/python3

"""
DHT22 driver
YF Robotics Laboratory (http://www.yfrl.org)
"""

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT


def getDHTSensorData():
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 7)

    # handle exception
    if RH is None:
        RH = -1
    if T is None:
        T = -1

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
