# Raspberry Pi Environmental Sensing

This project is a personal sensing station that uses Raspberry Pi, a HTU21D, a AM2306 and a PMS7003 to get indoor/outdoor temperature, humidity and dust level. It also supports options to log measured data locally and/or submit to a MQTT broker, a remote MySQL database or Blynk.

- Raspberry Pi is a popular open-source hardware. This program is tested on RPi Zero W, but should support all versions of RPi.
- HTU21D is a digital temperature + humidity sensor and it is connected to RPi via I2C_1.
- AM2306 is an outdoor temperature + humidity sensor, which uses the DHT22 chip.
- PMS7003 is a laser dust sensor. It connects to the RPi using the serial port.
- MQTT is a subscribe/publish message protocol.
- MySQL is a SQL database.
- Blynk is an IoT platform that supports customization through its mobile phone app.


## 1. Requirements

- Python >= 3.5
- To use AM2306/DHT22:
  - RPi.GPIO: `sudo apt-get install python-rpi.gpio`
  - Adafruit driver: https://github.com/adafruit/Adafruit_Python_DHT
- To report to MQTT broker: https://pypi.org/project/paho-mqtt/#id3
- To report to MySQL server: `sudo apt-get install python3-pymysql`


## 2. Usage

1. Change to home directory: `cd ~`
2. Clone project: `git clone https://github.com/automaticdai/rpi-environmental-sensing`
3. Edit the configuration file `rpi-weather-config.json.json` and save
4. Copy the configuration to etc: `sudo cp rpi-weather-config.json /etc/rpi-weather-config.json`
5. Run the main script: `python3 main.py`


## 3. System Configuration

For the configuration file `config.json`:

### Config

- `sensor_id`: assign a sensor ID to the device.
- `log_on`: enable writing to the local log.
- `report_periodic`: run the script periodically / or only run one time.
- `report_interval_sec`: set the report interval (in second). If 'report_periodic' is false, this parameter will be ignored.

### MQTT

- `enable`: enable report to MQTT.
- `server`, `port`: broker IP and port.

### MySQL

- `enable`: enable report to MySQL.
- `host`, `port`: database IP and port.
- `user`, `password`: login user information.
- `db`, `table`: database and table name (should be an existed database).

### Blynk

- `enable`: enable report to Blynk
- `auth`: authentication key


## 4. Credit

- The HTU21D and DHT22 drivers are based on code from Adafruit.
