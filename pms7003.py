#!/usr/bin/python3

'''
PMS7003 driver
- PM1.0, PM2.5 and PM10.0 concentration in both standard & enviromental units
- Particulate matter per 0.1L air, categorized into 0.3um, 0.5um, 1.0um, 2.5um, 5.0um and 10um size bins

YF Robotics Laboratory
(http://www.yfrl.org)

Credit:
This code is based on: https://github.com/tomek-l/pms7003/
'''

import serial
from collections import OrderedDict
from pprint import pprint

class PMSSensorException(Exception):
    """
    Implies a problem with sensor communication that is unlikely to re-occur (e.g. serial connection glitch).
    Prevents from returning corrupt measurements.
    """
    pass

START_SEQ = bytes([0x42, 0x4d])
FRAME_BYTES = 30

#'.' are replaced with '_' for easier database compability
BYTES_MEANING = {
    1  : 'pm1_0',
    2  : 'pm2_5',
    3  : 'pm10_0',
    4  : 'pm1_0_atm',
    5  : 'pm2_5_atm',
    6  : 'pm10_0_atm',
    7  : 'pcnt_0_3',
    8  : 'pcnt_0_5',
    9  : 'pcnt_1_0',
    10 : 'pcnt_2_5',
    11 : 'pcnt_5_0',
    12 : 'pcnt_10_0',
}

VALUES = list(BYTES_MEANING.values())
NO_VALUES = len(BYTES_MEANING) + 1


class PMS7003Sensor:
    def __init__(self, serial_device):
        #values according to product data manual
        self._serial = serial.Serial(port=serial_device, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2)


    def _get_frame(self):
        """
        :return: a frame as a list of integer values of bytes
        """
        self._serial.read_until(START_SEQ)
        frame = list(self._serial.read(FRAME_BYTES))
        if len(frame) == FRAME_BYTES:
            return frame
        else:
            raise PMSSensorException


    def _parse_frame(self, f):
        """
        iterates every second index and glues the H and L bytes together
        :return: raw parsed integer values
        """
        vls = [f[i]<<8 | f[i+1] for i in range(0, len(f), 2)]
        return vls


    def _valid_frame(self, frame, vls):
        _checksum = vls[-1]
        return _checksum == sum(frame[:-2]) + sum(START_SEQ)


    def read(self, ordered=False):
        """
        :return: a dict with measurements or raises PMS7003Exception in case of a problem with connection
        """
        frame = self._get_frame()
        values = self._parse_frame(frame)
        #frame_len = values[0] (you could read the frame length from here)

        if self._valid_frame(frame, values):
            if ordered:
                return OrderedDict((BYTES_MEANING[i], values[i]) for i in range(1, NO_VALUES))
            else:
                return {BYTES_MEANING[i]: values[i] for i in range(1, NO_VALUES)} #(regular dict)
        else:
            raise PMSSensorException


    def close(self):
        self._serial.close()


# call main
if __name__ == '__main__':

    sensor = PMS7003Sensor('/dev/ttyS0')

    while True:
        try:
            reading = sensor.read()
            print(reading['pm2_5'])
            print(reading['pm10_0'])
        except PMSSensorException:
            print('Connection problem')

    sensor.close()
