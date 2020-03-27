#!/usr/bin/python3

'''
PMS7003 driver
YF Robotics Laboratory (http://www.yfrl.org)

Credit:
This code is based on: https://github.com/tomek-l/pms7003/
'''

import serial
from collections import OrderedDict


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
    1 : 'pm1_0cf1',
    2 : 'pm2_5cf1',
    3 : 'pm10cf1',
    4 : 'pm1_0',
    5 : 'pm2_5',
    6 : 'pm10',
    7 : 'n0_3',
    8 : 'n0_5',
    9 : 'n1_0',
    10: 'n2_5',
    11 : 'n5_0',
    12 : 'n10',
}

VALUES = list(BYTES_MEANING.values())
NO_VALUES = len(BYTES_MEANING) + 1

START_BYTE_1 = 0x42
START_BYTE_2 = 0x4d

PMS_FRAME_LENGTH = 0
PMS_PM1_0 = 1
PMS_PM2_5 = 2
PMS_PM10_0 = 3
PMS_PM1_0_ATM = 4
PMS_PM2_5_ATM = 5
PMS_PM10_0_ATM = 6
PMS_PCNT_0_3 = 7
PMS_PCNT_0_5 = 8
PMS_PCNT_1_0 = 9
PMS_PCNT_2_5 = 10
PMS_PCNT_5_0 = 11
PMS_PCNT_10_0 = 12
PMS_VERSION = 13
PMS_ERROR = 14
PMS_CHECKSUM = 15

class PMS7003Sensor:

    def __init__(self, serial_device):
        #values according to product data manual
        self._serial = serial.Serial(port=serial_device, baudrate=9600, bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2)
        print(self._serial.name)

    def _get_frame(self):
        """
        :return: a frame as a list of integer values of bytes
        """
        with self._serial as s:
            s.read_until(START_SEQ)
            frame = list(s.read(FRAME_BYTES))
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
        :return: a dict with measurements or raises Pms7003Exception in case of a problem with connection
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
            print(sensor.read())
        except PMSSensorException:
            print('Connection problem')

    sensor.close()
