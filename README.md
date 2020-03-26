# Raspberry Pi Environmental Sensing

This project is a personal sensing station that uses Raspberry Pi, a HTU21, a DHT 22 and a PM sensor to get indoor temperature and humidity. It supports options to submit measured data to a remote MySQL database or Blynk.

- Raspberry Pi is a popular open-source hardware. This program is tested on RPi Zero W, but should support all versions of RPi.
- HTU21D is a digital temperature + humidity sensor and it is connected to RPi via I2C_1.
- AM2306 is an outdoor temperature + humidity sensor, which uses DHT22.
- Blynk is an IoT platform that supports customization through its mobile phone app.

---

## Requirements

- Python > 3.5
- RPi.gpio: `sudo apt-get install python-rpi.gpio`
- To use HTU21: Adafruit_DHT
- To report to MySQL server: `sudo apt-get install python3-pymysql`
- To use AM2306/DHT22: https://github.com/adafruit/Adafruit_Python_DHT

---

## Usage

1. Change to home directory: `cd ~`
2. Clone project: `git clone https://github.com/automaticdai/rpi-indoor-environment-sensing`
3. Copy configuration from template: `cp config_template.json config.json`
4. Edit the configuration file `config.json` and save
5. Run the main script: `python3 main.py`

---

## System Configuration

For the configuration file `config.json`:

### Options

- 'sensor_id': assign a sensor ID to the device.
- 'report_periodic': run the script periodically / or only run one time.
- 'report_interval_sec': set the report interval (in second). If 'report_periodic' is false, this parameter will be ignored.


### Blynk

- 'enable': enable report to Blynk
- 'auth': authentication key


### MySQL

- 'enable': enable report to MySQL.
- 'host', 'port': database IP and port.
- 'user', 'password': login user information.
- 'db', 'table': database and table name (should be an existed database).

---

## Credit

The IIC and HTU21D drivers are based on code from Adafruit.
