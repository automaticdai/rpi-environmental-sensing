# rpi-indoor-weather-sensing

## Introduction
This is a personal indoor weather station that uses Raspberry Pi and HTU21 to get indoor temperature and humidity. Also support options to submit measured data to InitialState, Yeelink or a remote MySQL database.

- HTU21D is a digital temperature + humidity sensor and it is connected to RPi by iic.
- Raspberry Pi is a popular open-source hardware. This program is tested on RPi 1B, but should support all versions of RPi.

## Requirement
- python 3
- You will need Python Data Streamer (http://github.com/InitialState/python_appender) if data need to be reported to Initialstate.

## Usage
1. ```git clone https://github.com/automaticdai/rpi-indoor-environment-sensing```

2. ```cp config_template.json config.json```

3. Change configuration file and save: ```vim config.json```

4. Run script: ```python3 main.py```

## Configuration
### System Configuration
- 'report_only_once': the script will be only ran once.
- 'report_interval_sec': set the report period in second. If report_only_once is true, this parameter is ignored.

### Yeelink
- 'enable': enable functionality.
- 'api_key': developer API key from Yeelink.
- 'xxxx_url': the device API address, e.g., "/v1.0/device/3365/sensor/387420/datapoints".

### InitialState
- 'enable': enable functionality.
- 'bucket_name', 'bucket_key': bucket name and key from your data bucket.
- 'access_key': provided by InitialState.

### MySQL
- 'enable': enable report to MySQL.
- 'host', 'port': database IP and port.
- 'user', 'password': login user information.
- 'db', 'table': database and table name (should be an existed database).
