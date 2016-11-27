#!/usr/bin/python3
import htu21d

if __name__ == "__main__":
    obj = htu21d.HTU21D()
    print("Temp: %s C" % obj.read_temperature())
    print("Humid: %s %% rH" % obj.read_humidity())
