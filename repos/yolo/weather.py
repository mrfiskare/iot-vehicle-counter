import re

import requests
from datetime import datetime
import pytz

class WeatherAPI:
    def __init__(self, iso_datetime):
        self.iso_datetime = iso_datetime
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_unixtime(self):
        dt = datetime.fromisoformat(self.iso_datetime)
        dt = dt.replace(minute=0)
        unixtime = dt.replace(tzinfo=pytz.UTC).timestamp()
        return int(unixtime)


    def get_weather_data(self):
        iso_date = self.iso_datetime.split('T')[0]  # get the date part
        params = {
            "latitude": 46.07,
            "longitude": 18.23,
            "hourly": "temperature_2m,precipitation",
            "timeformat": "unixtime",
            "start_date": iso_date,
            "end_date": iso_date
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()
        return data

    def get_weather_at_timestamp(self):
        data = self.get_weather_data()
        timestamp = self.get_unixtime()
        if 'hourly' in data and 'time' in data['hourly']:
            try:
                idx = data['hourly']['time'].index(timestamp)
                return idx
            except ValueError:
                return None
        else:
            return None

    def get_temperature(self):
        idx = self.get_weather_at_timestamp()
        if idx is not None:
            temperature = self.get_weather_data()['hourly']['temperature_2m'][idx]
            return temperature
        return None

    def get_precipitation(self):
        idx = self.get_weather_at_timestamp()
        if idx is not None:
            precipitation = self.get_weather_data()['hourly']['precipitation'][idx]
            return precipitation
        return None


# Test

api = WeatherAPI('2023-05-18T21:12:00+01:16')
print(api.get_temperature())
print(api.get_precipitation())
