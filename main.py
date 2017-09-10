#!/usr/bin/python3
'''
- Author: Yunfei Robotics Laboratory
- Website: http://www.yfworld.com
- Version: v0.3
- Updated: 26 Nov 2016
- Note:
  This code collects environmental data from a HTU21D sensor on a Raspberry Pi
  and report it to MySQL, Yeelink and/or Inital State. HTU21D is a temperature
  and humidity sensor. It is connected to RPi via I2C_1 bus.
- Credit:
  The IIC and HTU21D drivers are based on code from Adafruit.
'''

import time, datetime, json, http.client, htu21d
import urllib.request
from pprint import pprint

sensor_id = 0

def initial_report(temp, humi, config):
    from ISStreamer.Streamer import Streamer
    streamer = Streamer(bucket_name=config["bucket_name"],
                bucket_key=config["bucket_key"],
                access_key=config["access_key"])
    streamer.log("Temperature", round(temp,1))
    streamer.log("Humidity", round(humi,1))
    print("Initial State Committed")


def mysql_commit(temp, humid, config):
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
            s_temp = "%.2f" % temp
            s_humid = "%.2f" % humid
            cursor.execute(sql, (sensor_id, s_temp, s_humid))

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

    try:
        conn = http.client.HTTPConnection("api.yeelink.net", timeout=10)
        conn.request("POST", config["temperature_url"], params_temp, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)

        conn.request("POST", config["humidity_url"], params_humi, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)

        conn.close()
    except:
        pass


if __name__ == "__main__":
    # load configs from .json file
    with open('/home/pi/workspace/pi-indoor-weather-sensing/config.json') as config_file:
        config = json.load(config_file)

        system_cfg = config["config"]
        sensor_id = system_cfg["sensor_id"]

        yeelink_cfg = config["Yeelink"]
        initstate_cfg = config["InitialState"]
        mysql_cfg = config["MySQL"]

        # print configuration
        #pprint(config)
        #pprint(yeelink_cfg)
        #pprint(initstate_cfg)
        #pprint(mysql_cfg)

    # create a sensor object
    sensor = htu21d.HTU21D()

    # infinite loop goes here
    while (True):
        print(">>>>>>>>>>")

        # print current time stamp and sensor data
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)

        # read sensor data from HTU21D sensor
        temp = sensor.read_temperature()
        humi = sensor.read_humidity()
        print("Temperature: %.2f C" % temp)
        print("Humidity: %.2f %% rH" % humi)

        # report to remote services
        if (yeelink_cfg["enable"] == True):
            yeelink_report(st, temp, humi, yeelink_cfg)

        if (initstate_cfg["enable"] == True):
            initial_report(temp, humi, initstate_cfg)

        if (mysql_cfg["enable"] == True):
            mysql_commit(temp, humi, mysql_cfg)

        response = urllib.request.urlopen('http://blynk-cloud.com/75a958a9a9224295afd691cb303e428d/update/V0?value=' + ("%.2f" % temp))
        response = urllib.request.urlopen('http://blynk-cloud.com/75a958a9a9224295afd691cb303e428d/update/V1?value=' + ("%.2f" % humi))
        response = urllib.request.urlopen('http://blynk-cloud.com/75a958a9a9224295afd691cb303e428d/update/V2?value=' + ("%s" % st).replace(" ","_"))

        print("<<<<<<<<<<")

        # report once or periodically is defined by config 'report_only_once'
        if (system_cfg["report_only_once"] == True):
            break
        else:
            # sleep for 'report_interval_second'
            time.sleep(system_cfg["report_interval_sec"])
