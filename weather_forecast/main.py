#!/usr/bin/python3

import pywapi
import pprint
import time
import sys

# -- Confiurations  ------------------------------------------------------------
# change the city name to  yours
CITY_NAME = 'York, YOR, United Kingdom'

# -- Fetch Weather Information
def fetch_weather():
     # find the city_id from weather.com

    #city_list = pywapi.get_loc_id_from_weather_com(CITY_NAME)
    #city_id = city_list[0][0]
    city_id = "UKXX0162"

    # retrive weather data from weather.com
    weather_info = pywapi.get_weather_from_weather_com(city_id)

    # print raw data (debug only)
    print('\nRaw Retrived Data:')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(weather_info)

    # get units
    units = {}
    units['distance'] = weather_info['units']['distance']
    units['pressure'] = weather_info['units']['pressure']
    units['rainfall'] = weather_info['units']['rainfall']
    units['speed'] = weather_info['units']['speed']
    units['temperature'] = weather_info['units']['temperature']

    # output current condition
    print('[City]')
    print(weather_info['location']['name'])
    print('\n[Current]')
    print('Description: ' + weather_info['current_conditions']['text'])
    print('Temperature: ' + weather_info['current_conditions']['temperature'] \
			+ ' ' + units['temperature'])
    print('Humidity: ' + weather_info['current_conditions']['humidity'] +'%')
    print(weather_info['current_conditions']['wind'])

    # forecasts
    print('\n[Forecast]')
    for i in weather_info['forecasts']:
            print(i['date'] + ',' + i['day_of_week'] + ': ' \
                + i['day']['brief_text'] + ', ' \
                + i['low'] + '-' + i['high'] + ' ' + units['temperature'])

    # package data into a string
    weather_str = weather_info['location']['name'] + ';' \
            + 'Now: ' + weather_info['current_conditions']['text'] + ';' \
            + 'Temp: ' + weather_info['current_conditions']['temperature'] + ' C;' \
            + 'Humid: ' + weather_info['current_conditions']['humidity'] + ' %;' \
            + 'Today: ' + weather_info['forecasts'][0]['low'] + ' - ' \
            + weather_info['forecasts'][0]['high'] + ';\n'

    return weather_str


# -- Main Program  -------------------------------------------------------------
if __name__ == "__main__":
    weather_str = fetch_weather()
    print(weather_str)
