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


flag_connected = True

def _on_connect(client, userdata, message, rc):
    """
    Called when the broker responds to our connection request.

    @param client:
        the client instance for this callback
    @param userdata:
        the private user data as set in Client() or userdata_set()
    @param message:
        response message sent by the broker
    @param rc:
        the connection result
    """
    global flag_connected

    if rc == 0:
        errtext="Connection successful"
    elif rc == 1:
        errtext="Connection refused: Unacceptable protocol version"
    elif rc == 2:
        errtext="Connection refused: Identifier rejected"
    elif rc == 3:
        errtext="Connection refused: Server unavailable"
    elif rc == 4:
        errtext="Connection refused: Bad user name or password"
    elif rc == 5:
        errtext="Connection refused: Not authorized"
    else:
        errtext="Connection refused: Unknown reason"

    flag_connected = True
    logging.info("MQTT on_connect() returns rc={}: {}".format(rc, errtext))


def _on_disconnect(client, userdata, rc):
    global flag_connected

    flag_connected = False
    logging.info("MQTT on_disconnect() triggered!")


if __name__ == "__main__":
    # load configs from .json file
    with open('/etc/rpi-weather-config.json') as config_file:
        config = json.load(config_file)

        system_cfg = config["config"]
        mqtt_cfg = config["MQTT"]
        mysql_cfg = config["MySQL"]

        # print configuration
        pprint(config)

    if system_cfg["log_to_file"] == True:
        # define a Handler that writes INFO messages to a log file
        logging.basicConfig(level=logging.INFO,
                            filename='log.txt',
                            filemode='a',
                            format='[%(asctime)s-%(levelname)s: %(message)s]',
                            datefmt='%Y-%m-%d %H:%M:%S')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    else:
        # define a Handler which writes INFO messages or higher to the sys.stderr
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s-%(levelname)s: %(message)s]',
                            datefmt='%Y-%m-%d %H:%M:%S')

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

        client = mqtt.Client()
        client.on_connect = _on_connect
        client.on_disconnect = _on_disconnect
        try:
            client.connect(mqtt_server, mqtt_port, 60)
            logger = logging.getLogger(__name__)
            client.enable_logger(logger)
        except:
            logging.error("MQTT initialized failed!")
            sys.exit(1)

    # infinite loop goes here
    while True:
        logging.info(">>>>>>>>>>>>>>>>>>>>")

        # print current time stamp and sensor data
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        logging.info(st)

        try:
            # read sensor data from HTU21D sensor
            temp = round( htu.read_temperature(), 2 )
            humid = round( htu.read_humidity(), 2 )

            # read sensor data from AM2306
            temp_out, humid_out = dht22.getDHTSensorData()
            temp_out = round(temp_out, 2)
            humid_out = round(humid_out, 2)

            # read data from PMS7003
            reading = pms.read()
            pm2_5 = reading['pm2_5']
            pm10 = reading['pm10_0']
        except htu21d.HTUSensorException:
            logging.error("HTU read failed!")
            time.sleep(1)
            continue
        except dht22.DHTSensorException:
            logging.error("AM2306 read failed!")
            time.sleep(1)
            continue
        except pms7003.PMSSensorException:
            logging.error("PMS7003 read failed!")
            time.sleep(1)
            continue
        except:
            logging.error("Unknown Exception!")
            traceback.print_exec()
            time.sleep(1)
            continue
        else:
            logging.info("Temperature: %.2f C" % temp)
            logging.info("Humidity: %.2f %%rH" % humid)
            logging.info("Temperature(outdoor): %.2f C" % temp_out)
            logging.info("Humidity(outdoor): %.2f %%rH" % humid_out)
            logging.info("PM2.5: %d" % pm2_5)
            logging.info("PM10: %d" % pm10)
        finally:
            pass

        # report to MQTT
        if mqtt_cfg["enable"] == True:
            if flag_connected == False:
                try:
                    # reconnect
                    client.connect(mqtt_server, mqtt_port, 60)
                    logging.info("MQTT reconnect triggered.")
                except:
                    logging.error("MQTT reconnect failed!")
            try:
                client.publish(sensor_name + "/Timestamp", st)
                client.publish(sensor_name + "/Temp", temp)
                client.publish(sensor_name + "/Humid", humid)
                client.publish(sensor_name + "/Temp_out", temp_out)
                client.publish(sensor_name + "/Humid_out", humid_out)
                client.publish(sensor_name + "/PM2_5", pm2_5)
                client.publish(sensor_name + "/PM10", pm10)
            except:
                logging.error("MQTT communication error!")
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

        # loop the MQTT client
        client.loop()
