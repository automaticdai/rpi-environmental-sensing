#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
RPi Environmental Sensing
Yunfei Robotics Laboratory (http://www.yfrl.org)
Version 1.0 (26 March 2020)
"""

import sys, time, datetime, json
import traceback
import htu21d
import dht22
import pms7003
import urllib.request
import http.client
from pprint import pprint
# comment if you do not use the following packages
import pymysql.cursors
import paho.mqtt.client as mqtt
import logging

def mysql_commit(sensor_id, temp, humid, temp_ex, humid_ex, config):
    # Connect to the database
    try:
        connection = pymysql.connect(host=config['host'],
                                 user=config['user'],
                                 password=config['password'],
                                 db=config['db'],
                                 charset=config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `WEATHER_MEASUREMENT` (`SENSOR_ID`, `IN_TEMP`, \
                `IN_HUMID`, `EX_TEMP`, `EX_HUMID`) VALUES (%s, %s, %s, %s, %s)"
            s_temp = "{:.2f}".format(temp)
            s_humid = "{:.2f}".format(humid)
            s_temp_ex = "{:.2f}".format(temp_ex)
            s_humid_ex = "{:.2f}".format(humid_ex)
            cursor.execute(sql, (sensor_id, s_temp, s_humid, s_temp_ex, s_humid_ex))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        print("Database Committed")
    except:
        pass
    finally:
        connection.close()


if __name__ == "__main__":
    # load configs from .json file
    with open('/etc/rpi-weather-config.json') as config_file:
        config = json.load(config_file)

        system_cfg = config["config"]
        mqtt_cfg = config["MQTT"]
        mysql_cfg = config["MySQL"]

        # print configuration
        pprint(config)

    # enable logger
    LOG_FORMAT = '[%(asctime)s-%(levelname)s: %(message)s]'
    LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
    if system_cfg["log_to_file"] == True:
        logging.basicConfig(filename='log.txt', filemode='a', level=logging.INFO,
                            format=LOG_FORMAT, datefmt=LOG_DATEFMT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATEFMT)

    # read sensor id & name
    sensor_id = system_cfg["sensor_id"]
    sensor_name = system_cfg["sensor_name"]

    # create a sensor object
    try:
        htu = htu21d.HTU21D()
    except:
        print("[Error] HTU21D initialized failed!")
        traceback.print_exc()
        sys.exit(1)

    # create a PMS object
    try:
        pms = pms7003.PMS7003Sensor('/dev/ttyS0')
    except:
        print("[Error] PMS7003 initialized failed!")
        traceback.print_exc()
        sys.exit(1)

    # connect to MQTT
    if mqtt_cfg["enable"] == True:
        mqtt_server = mqtt_cfg["server"]
        mqtt_port = mqtt_cfg["port"]

        try:
            client = mqtt.Client()
            client.connect(mqtt_server, mqtt_port, 60)
            logger = logging.getLogger(__name__)
            client.enable_logger(logger)
        except:
            logging.error("[Error] MQTT initialized failed!")
            traceback.print_exc()
            sys.exit(1)

    # infinite loop goes here
    while True:
        logging.info(">>>>>>>>>>>>>>>>>>>>")
        print(".", end='')

        # loop the MQTT client
        if mqtt_cfg["enable"] == True:
            try:
                client.loop()
            except:
                traceback.print_exc()

        # print current time stamp and sensor data
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        logging.info(st)

        # read sensor data from HTU21D sensor
        try:
            temp = round( htu.read_temperature(), 2 )
            humid = round( htu.read_humidity(), 2 )
            logging.info("Temperature: %.2f C" % temp)
            logging.info("Humidity: %.2f %%rH" % humid)
        except:
            logging.error("[Error] HTU read failed!")
            continue

        # read sensor data from AM2306
        try:
            temp_out, humid_out = dht22.getDHTSensorData()
            temp_out = round(temp_out, 2)
            humid_out = round(humid_out, 2)
            logging.info("Temperature(outdoor): %.2f C" % temp_out)
            logging.info("Humidity(outdoor): %.2f %%rH" % humid_out)
        except:
            logging.error("[Error] AM2306 read failed!")
            continue

        # read data from PMS7003
        try:
            reading = pms.read()
            pm2_5 = reading['pm2_5']
            pm10 = reading['pm10_0']
            logging.info("PM2.5: %d" % pm2_5)
            logging.info("PM10: %d" % pm10)
        except:
            logging.error("[Error] PMS7003 read failed!")
            continue

        # report to MQTT
        if mqtt_cfg["enable"] == True:
            try:
                client.publish(sensor_name + "/Timestamp", st)
                client.publish(sensor_name + "/Temp", temp)
                client.publish(sensor_name + "/Humid", humid)
                client.publish(sensor_name + "/Temp_out", temp_out)
                client.publish(sensor_name + "/Humid_out", humid_out)
                client.publish(sensor_name + "/PM2_5", pm2_5)
                client.publish(sensor_name + "/PM10", pm10)
            except:
                traceback.print_exec()

        # report to MySQL
        if mysql_cfg["enable"] == True:
            mysql_commit(sensor_id, temp, humid, temp_out, humid_out, mysql_cfg)

        # report once or periodically is defined by config 'report_only_once'
        if system_cfg["report_periodic"] == True:
            # sleep for (report_period - elapsed_time)
            ts_diff = time.time() - ts
            interval = max(int(system_cfg["report_interval_sec"] - ts_diff), 0)
            time.sleep(interval)
        else:
            # exit
            sys.exit(0)
