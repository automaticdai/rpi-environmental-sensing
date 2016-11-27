# pi-indoor-weather-sensing

## Introduction
This is a personal indoor weather station that uses Raspberry Pi and HTU21D to sense indoor temperatue and humidity. Also support options to submit measured data to Initial State, Yeelink or a remote MySQL database.

HTU21D is a temperature + humidity sensor and it is connected to RPi by iic.


## Requirement
- python3


## Usage
1. ```cp config_template.json config.json```

2. Change configuration file and save: ```vim config.json```

3. Run script: ```python3 main.py```
``````
