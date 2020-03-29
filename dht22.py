#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
DHT22 driver
YF Robotics Laboratory (http://www.yfrl.org)
"""

import sys
import RPi.GPIO as GPIO
import Adafruit_DHT


class DHTSensorException(Exception):
    pass


def getDHTSensorData():
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 7)

    # handle exception
    if (RH is not None) and (T is not None):
        return (T, RH)
    else:
        raise DHTSensorException


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
