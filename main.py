#!/usr/bin/python3

'''
- Yunfei Robotics Laboratory (http://www.yfrl.org)
- v1.0 (26 March 2020)
'''

import time, datetime, json, http.client, htu21d, dht22
import urllib.request
from pprint import pprint

sensor_id = 0


def mysql_commit(temp, humid, temp_ex, humid_ex, config):
    import pymysql.cursors
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
            sql = "INSERT INTO `WEATHER_MEASUREMENT` (`SENSOR_ID`, `IN_TEMP`, `IN_HUMID`, `EX_TEMP`, `EX_HUMID`) VALUES (%s, %s, %s, %s, %s)"
            s_temp = "%.2f" % temp
            s_humid = "%.2f" % humid
            s_temp_ex = "%.2f" % temp_ex
            s_humid_ex = "%.2f" % humid_ex
            cursor.execute(sql, (sensor_id, s_temp, s_humid, s_temp_ex, s_humid_ex))

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
    with open('/home/pi/rpi-indoor-environment-sensing/config.json') as config_file:
        config = json.load(config_file)

        system_cfg = config["config"]
        sensor_id = system_cfg["sensor_id"]

        yeelink_cfg = config["Yeelink"]
        initstate_cfg = config["InitialState"]
        mysql_cfg = config["MySQL"]
        blynk_cfg = config["Blynk"]

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

        # read sensor data from AM2306
        temp_out, humi_out = dht22.getDHTSensorData()
        print("Temperature(outdoor): %.2f C" % temp_out)
        print("Humidity(outdoor): %.2f %% rH" % humi_out)

        # report to remote services
        if (mysql_cfg["enable"] == True):
            mysql_commit(temp, humi, temp_out, humi_out, mysql_cfg)

        if (blynk_cfg["enable"] == True):
            blynk_report()
            baseurl = 'http://blynk-cloud.com/' + blynk_cfg["auth"]
            blynk_report('V0', ("%.2f" % temp), blynk_cfg)
            blynk_report('V1', ("%.2f" % humi), blynk_cfg)
            blynk_report('V2', ("%s" % st).replace(" ","_"), blynk_cfg)
            blynk_report('V3', ("%.2f" % temp_out), blynk_cfg)
            blynk_report('V4', ("%.2f" % humi_out), blynk_cfg)

        print("<<<<<<<<<<")

        # report once or periodically is defined by config 'report_only_once'
        if (system_cfg["report_periodic"] == True):
            # sleep for 'report_interval_second'
            time.sleep(system_cfg["report_interval_sec"])
        else:
            break
