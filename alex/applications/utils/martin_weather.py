#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib
from datetime import datetime
from datetime import time as dttime
import json
import time

from alex.utils.config import load_as_module
from alex.tools.apirequest import APIRequest
from alex.utils.cache import lru_cache


class Weather(object):
    pass

class WeatherPoint(object):
    def __init__(self, in_city=None, in_state=None):
        self.in_city = in_city if not in_city is 'none' else None
        self.in_state = in_state if not in_state is 'none' else None

class OpenWeatherMapWeather(Weather):

    def __init__(self, input_json, condition_transl, date=None, daily=False, celsius=True):
        # get current weather
        self.celsius = celsius

        if date is None:
            self.temp = self._round_temp(input_json['main']['temp'])
            self.condition = condition_transl[input_json['weather'][0]['id']]
            return
        # get prediction
        if daily:  # set time to 13:00 for daily
            date = datetime.combine(date.date(), dttime(13, 00))
        date = datetime.utcfromtimestamp(int(time.mktime(date.timetuple())))
        ts = int(date.strftime("%s"))  # convert time to Unix timestamp
        for fc1, fc2 in zip(input_json['list'][:-1], input_json['list'][1:]):
            # find the appropriate time frame
            if ts >= fc1['dt'] and ts <= fc2['dt']:
                self.condition = condition_transl[fc1['weather'][0]['id']]
                # hourly forecast -- interpolate temperature
                if not daily:
                    slope = (fc2['main']['temp'] - fc1['main']['temp']) / (fc2['dt'] - fc1['dt'])
                    self.temp = self._round_temp(fc1['main']['temp'] + slope * (ts - fc1['dt']))
                # daily forecast: use daily high & low
                else:
                    self.temp = self._round_temp(fc1['temp']['day'])
                    self.min_temp = self._round_temp(fc1['temp']['min'])
                    self.max_temp = self._round_temp(fc1['temp']['max'])
                break
        if not hasattr(self, 'temp'):
            self.temp = self._round_temp(input_json['list'][0]['main']['temp'])
            self.condition = condition_transl[input_json['list'][0]['weather'][0]['id']]

    def _round_temp(self, temp):
        if self.celsius:
            return int(round(temp - 273.15))
        else:
            return int(round((temp - 273.15) * 1.8 + 32))

    def __repr__(self):
        ret = self.condition + ', '
        if hasattr(self, 'min_temp'):
            ret += str(self.min_temp) + ' – ' + str(self.max_temp)
        else:
            ret += str(self.temp)

        units = ' °C' if self.celsius else ' °F'
        return ret + units

class WeatherFinder(object):
    """Abstract ancestor for transit direction finders."""

    def get_weather(self, time=None, daily=False, place=None):
        """
        Retrieve the weather for the given time, or for now (if time is None).

        Should be implemented in derived classes.
        """
        raise NotImplementedError()


class OpenWeatherMapWeatherFinder(WeatherFinder, APIRequest):
    """Weather service using OpenWeatherMap (http://openweathermap.org)"""

    def __init__(self, cfg):
        WeatherFinder.__init__(self)
        APIRequest.__init__(self, cfg, 'openweathermap', 'OpenWeatherMap query')
        self.weather_url = 'http://api.openweathermap.org/data/2.5/'

        self.celsius = True if cfg['weather']['units'] == 'celsius' else False
        self.suffix = cfg['weather']['suffix']
        self.load(cfg['weather']['dictionary'])

    def load(self, file_name):
        tp_mod = load_as_module(file_name, force=True)
        if not hasattr(tp_mod, 'CONDITION_TRANSL'):
            raise Exception("Weather config does not define the 'CONDITION_TRANSL' object!")

        self.condition_transl = tp_mod.CONDITION_TRANSL

    @lru_cache(maxsize=10)
    def get_weather(self, time=None, daily=False, city=None, state=None, lat=None, lon=None):
        """Get OpenWeatherMap weather information or forecast for the given time.

        The time/date should be given as a datetime.datetime object.
        """
        data = {}
        # prefer using longitude and latitude, if they are set
        if lat is not None and lon is not None:
            data['lat'] = lat
            data['lon'] = lon
        else:
            # if no state is specified get default state, city is optional
            state = state if state is not None else self.suffix
            query = ','.join([city, state]) if city is not None else state
            # set the city
            data['q'] = query.encode('utf-8')

        method = 'weather'
        if daily:
            method = 'forecast/daily'
        elif time is not None:
            method = 'forecast'

        self.system_logger.info("OpenWeatherMap request:\n" + method + ' + ' + str(data))

        page = urllib.urlopen(self.weather_url + method + '?' + urllib.urlencode(data))
        if page.getcode() != 200:
            return None
        response = json.load(page)
        self._log_response_json(response)
        if str(response['cod']) != "200":
            return None
        weather = OpenWeatherMapWeather(response, self.condition_transl, time, daily, celsius=self.celsius)
        self.system_logger.info("OpenWeatherMap response:\n" + unicode(weather))
        return weather
