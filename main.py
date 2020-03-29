#!/usr/bin/python3

'''
RPi Environmental Sensing
Yunfei Robotics Laboratory (http://www.yfrl.org)
Version 1.0 (26 March 2020)
'''

import time, datetime, json
import htu21d
import dht22
import pms7003
import urllib.request
import http.client
from pprint import pprint
# comment if you do not use the following packages
import pymysql.cursors
import paho.mqtt.client as mqtt


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
            s_temp = "%.2f" % temp
            s_humid = "%.2f" % humid
            s_temp_ex = "%.2f" % temp_ex
            s_humid_ex = "%.2f" % humid_ex
            cursor.execute(sql, (sensor_id, s_temp, s_humid, \
                            s_temp_ex, s_humid_ex))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        print("Database Committed")
    except:
        pass
    finally:
        connection.close()


def blynk_report(vpin_name_str, vpin_value_str, config):
    try:
        baseurl = 'http://blynk-cloud.com/' + config["auth"]
        url = baseurl + '/update/' + vpin_name_str + '?value=' + vpin_value_str
        response = urllib.request.urlopen(url)
    except:
        pass


if __name__ == "__main__":
    # load configs from .json file
    with open('/etc/rpi-weather-config.json') as config_file:
        config = json.load(config_file)

        system_cfg = config["config"]
        mqtt_cfg = config["MQTT"]
        mysql_cfg = config["MySQL"]
        blynk_cfg = config["Blynk"]

        # print configuration
        #pprint(config)

    # read sensor id & name
    sensor_id = system_cfg["sensor_id"]
    sensor_name = system_cfg["sensor_name"]

    # create a sensor object
    htu = htu21d.HTU21D()

    # create a PMS object
    pms = pms7003.PMS7003Sensor('/dev/ttyS0')

    # connect to MQTT
    if (mqtt_cfg["enable"] == True):
        mqtt_server = mqtt_cfg["server"]
        mqtt_port = mqtt_cfg["port"]

        client = mqtt.Client()
        #client.on_connect = on_connect
        #client.on_message = on_message

        client.connect(mqtt_server, mqtt_port, 60)

    # infinite loop goes here
    while (True):
        print(">>>>>>>>>>>>>>>>>>>>")

        # print current time stamp and sensor data
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)

        # read sensor data from HTU21D sensor
        temp = htu.read_temperature()
        humi = htu.read_humidity()
        print("Temperature: %.2f C" % temp)
        print("Humidity: %.2f %%rH" % humi)

        # read sensor data from AM2306
        temp_out, humi_out = dht22.getDHTSensorData()

        print("Temperature(outdoor): %.2f C" % temp_out)
        print("Humidity(outdoor): %.2f %%rH" % humi_out)

        reading = pms.read()
        pm2_5 = reading['pm2_5']
        pm10 = reading['pm10_0']
        print("PM2.5: %d" % pm2_5)
        print("PM10: %d" % pm10)

        # report to MQTT
        if (mqtt_cfg["enable"] == True):
            client.publish(sensor_name + "/Timestamp", st);
            client.publish(sensor_name + "/Temp", temp)
            client.publish(sensor_name + "/Humid", humi)
            client.publish(sensor_name + "/Temp_out", temp_out)
            client.publish(sensor_name + "/Humid_out", humi_out)
            client.publish(sensor_name + "/PM2_5", pm2_5)
            client.publish(sensor_name + "/PM10", pm10)

        # report to MySQL
        if (mysql_cfg["enable"] == True):
            mysql_commit(sensor_id, temp, humi, temp_out, humi_out, mysql_cfg)

        # report to Blynk
        if (blynk_cfg["enable"] == True):
            blynk_report()
            baseurl = 'http://blynk-cloud.com/' + blynk_cfg["auth"]
            blynk_report('V0', ("%.2f" % temp), blynk_cfg)
            blynk_report('V1', ("%.2f" % humi), blynk_cfg)
            blynk_report('V2', ("%s" % st).replace(" ","_"), blynk_cfg)
            blynk_report('V3', ("%.2f" % temp_out), blynk_cfg)
            blynk_report('V4', ("%.2f" % humi_out), blynk_cfg)

        print("<<<<<<<<<<<<<<<<<<<<")

        # report once or periodically is defined by config 'report_only_once'
        if (system_cfg["report_periodic"] == True):
            # sleep for (report_period - elapsed_time)
            ts_diff = time.time() - ts
            interval = max(int(system_cfg["report_interval_sec"] - ts_diff), 0)
            time.sleep(interval)
        else:
            break
