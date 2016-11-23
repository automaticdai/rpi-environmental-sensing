#!/usr/bin/python3
'''
- Author: Yunfei Robotics Laboratory
- Website: http://www.yfworld.com
- Version: v0.2
- Updated: 23 Nov 2016
- Note:
  This code collects environmental data from a HTU21D sensor on a Raspberry Pi
  and report it to MySQL, Yeelink and/or Inital State. HTU21D is a temperature
  and humidity sensor. It is connected to RPi via I2C_1 bus.
- Credit:
  The IIC and HTU21D drivers are based on code provided by Adafruit.
'''

import time, datetime, json, http.client, htu21d
from pprint import pprint

SENSOR_ID = 1

def initial_report(temp, humi, config):
    from ISStreamer.Streamer import Streamer
    streamer = Streamer(bucket_name=config["bucket_name"],
                bucket_key=config["bucket_key"],
                access_key=config["access_key"])
    streamer.log("Temperature", round(temp,1))
    streamer.log("Humidity", round(humi,1))
    print("Initial State Committed")


def mysql_commit(s_temp, s_humid, config):
    import pymysql.cursors
    # Connect to the database
    connection = pymysql.connect(host=config['host'],
                                 user=config['user'],
                                 password=config['password'],
                                 db=config['db'],
                                 charset=config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `WEATHER_MEASUREMENT` (`SENSOR_ID`, `IN_TEMP`, `IN_HUMID`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (SENSOR_ID, s_temp, s_humid))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        print("Database Committed")

    finally:
        connection.close()


def yeelink_report(st, temp, humi, config):
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain", "U-ApiKey": config["api_key"]}
    params_temp = "{\"timestamp\":\"%s\",\"value\":%.2f}" % (st, temp)
    params_humi = "{\"timestamp\":\"%s\",\"value\":%.2f}" % (st, humi)

    with http.client.HTTPConnection("api.yeelink.net", timeout=10) as conn:
        conn.request("POST", "/v1.0/device/1869/sensor/387420/datapoints", params_temp, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)

        conn.request("POST", "/v1.0/device/1869/sensor/387421/datapoints", params_humi, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)

        conn.close()


if __name__ == "__main__":
    # load configs from .json file
    with open('config.json') as config_file:
        config = json.load(config_file)

        yeelink_cfg = config["Yeelink"]
        initstate_cfg = config["InitialState"]
        mysql_cfg = config["MySQL"]
        system_cfg = config["config"]

        pprint(config)
        pprint(yeelink_cfg)
        pprint(initstate_cfg)
        pprint(mysql_cfg)

    # create a sensor object
    sensor = htu21d.HTU21D()

    # infinite loop goes here
    while (True):
        # read sensor data from HTU21D sensor
        temp = sensor.read_temperature()
        humi = sensor.read_humidity()

        # print current time stamp and sensor data
        print("----------")
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)
        print("Temp: %.2f C" % temp)
        print("Humid: %.2f %% rH" % humi)

        # report to remote services
        if yeelink_cfg["enable"]:
            yeelink_report(st, temp, humi, yeelink_cfg)

        if initstate_cfg["enable"]:
            initial_report(temp, humi, initstate_cfg)

        if mysql_cfg["enable"]:
            mysql_commit("%.2f" % temp, "%.2f" % humi, mysql_cfg)

        # sleep for 'report_interval_second'
        time.sleep(system_cfg["report_interval_sec"])
