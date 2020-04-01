#!/usr/bin/python

import os
import urllib2
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

# this is where you should put your OpenWeatherMap API key
# get your own key from http://openweathermap.org/
API_KEY = "5eb19937b8ba9aa2029fe7e290b8d799"

# this is the city you want to enquiry
CITY_NAME = "York,uk"

# get weather data from weather.com
try:
	f = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' \
                    + CITY_NAME + '&units=metric' + '&APPID=' +  API_KEY)
	respond_raw = f.read()
except:
        print 'Execption: URL is not correct!'
        raise

# unpack json package into python dictionary
weather_dict = json.loads(respond_raw)

# print raw data with pprint
pp.pprint(weather_dict)

# print human-readable weather message
print('\n\n' + weather_dict['name'] + ' is ' + \
      weather_dict['weather'][0]['description'] + \
      ', temperature: ' + str(weather_dict['main']['temp']) + \
      ', humidity: ' + str(weather_dict['main']['humidity']) + '%.' )
