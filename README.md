# RaspberryPi Indoor Environment Sensing
This project is a personal indoor weather station that uses Raspberry Pi and HTU21 to get indoor temperature and humidity. Also support options to submit measured data to InitialState, Yeelink or a remote MySQL database.

- HTU21D is a digital temperature + humidity sensor and it is connected to RPi by iic.
- Raspberry Pi is a popular open-source hardware. This program is tested on RPi 1B, but should support all versions of RPi.


## Requirement
- Python 3.5
- rpi.gpio: `sudo apt-get install python-rpi.gpio`
- To report to MySQL server: `sudo apt-get install python3-pymysql`
- To report to Initialstate, you will need Python Data Streamer (http://github.com/InitialState/python_appender).
- To use AM2306/DHT22, need DHT driver: https://github.com/adafruit/Adafruit_Python_DHT


## Usage
1. Change to home directory: `cd ~`
2. Clone project: `git clone https://github.com/automaticdai/rpi-indoor-environment-sensing`
3. Copy configuration from template: `cp config_template.json config.json`
4. Edit the configuration file `config.json` and save
5. Run the main script: `python3 main.py`


## Configuration
### System options
- 'report_periodic': run the script periodically / or only run one time.
- 'report_interval_sec': set the report period (in second). If 'report_periodic' is false, this parameter will be ignored.

### Yeelink
- 'enable': enable functionality.
- 'api_key': developer API key from Yeelink.
- 'xxxx_url': the device API address, e.g., "/v1.0/device/3365/sensor/387420/datapoints".

### InitialState
- 'enable': enable functionality.
- 'bucket_name', 'bucket_key': bucket name and key from your data bucket.
- 'access_key': provided by InitialState.

## Blynk
- 'enable'
- 'auth'

### MySQL
- 'enable': enable report to MySQL.
- 'host', 'port': database IP and port.
- 'user', 'password': login user information.
- 'db', 'table': database and table name (should be an existed database).
