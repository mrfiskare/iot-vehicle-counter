import os
import json
import serial
import time
import signal
import sys
import requests


class WeatherAPI:
    def __init__(self, iso_datetime):
        self.iso_datetime = iso_datetime
        self.api_key = ""
        self.lat = 46.071223
        self.lon = 18.211258
        self.weather_url = "http://api.openweathermap.org/data/2.5/weather"
        self.pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.units = "metric"
        self.measurement = {
            "timestamp": iso_datetime,
            "temperature": 0.0,
            "weather_category": "no rain or snow",
            "air_quality": 0
        }

    def get_weather_data(self):
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': self.units
        }
        response = requests.get(self.weather_url, params=params)
        return response.json()

    def get_pollution_data(self):
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': self.units
        }
        response = requests.get(self.pollution_url, params=params)
        return response.json()

    def get_aqi(self):
        pollution_data = self.get_pollution_data()
        if "list" in pollution_data and len(pollution_data["list"]) > 0:
            aqi = pollution_data["list"][0]["main"]["aqi"]
            print(f"Air Quality Index (AQI): {aqi}")
            return aqi
        else:
            print("No pollution data available.")
            return None

    @staticmethod
    def categorize_weather(description):
        if "rain" in description or "drizzle" in description:
            return "rain"
        elif "snow" in description:
            return "snow"
        else:
            return "no rain or snow"

    def check_precipitation(self):
        weather_data = self.get_weather_data()
        if "weather" in weather_data and len(weather_data["weather"]) > 0:
            description = weather_data["weather"][0]["description"].lower()
            category = self.categorize_weather(description)
            print(f"Weather category: {category}")
            return category
        else:
            print("No weather data available.")
            return "no rain or snow"

    def get_temperature(self):
        weather_data = self.get_weather_data()
        if "main" in weather_data:
            temperature = weather_data["main"]["temp"]
            print(f"Temperature: {temperature} °C")
            return temperature
        else:
            print("No temperature data available.")
            return None

    def read_weather_api(self):
        self.measurement["temperature"] = self.get_temperature()
        self.measurement["weather_category"] = self.check_precipitation()
        self.measurement["air_quality"] = self.get_aqi()
        return json.dumps(self.measurement)

    def save_to_file(self, data):
        json_folder = "/home/pi/json"
        json_file = "sensors.json"

        if not os.path.exists(json_folder):
            os.makedirs(json_folder)

        json_path = os.path.join(json_folder, json_file)

        data = []

        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                data = json.load(file)

        data.append({
            'timestamp': self.measurement['timestamp'],
            'temperature': self.measurement['temperature'],
            'weather_category': self.measurement["weather_category"],
            'air_quality': self.measurement["air_quality"]
        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()

        print(f"sensors.json -> "
              f"[{self.measurement['temperature']}°C, "
              f"{self.measurement['weather_category']}, "
              f"{self.measurement['air_quality']}] at "
              f"{self.measurement['timestamp']}")


if __name__ == "__main__":
    weather = WeatherAPI('2024-05-17T21:00:00+01:16')
    weather.check_precipitation()
    weather.get_aqi()
    weather.get_temperature()
