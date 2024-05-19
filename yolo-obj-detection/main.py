import os
import json
import glob
import shutil
import sys
import time
import datetime
import re
from pathlib import Path
from pytz import timezone
from vehicle_counter import *


def convert_to_iso(timestamp_str):
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M")
    timestamp = timestamp.replace(tzinfo=timezone('Europe/Budapest'))
    iso_timestamp = timestamp.isoformat()
    iso_timestamp = re.sub(r'\+\d{2}:\d{2}$', '', iso_timestamp)
    return iso_timestamp


def is_timestamp_present(data, timestamp_iso):
    for entry in data:
        if entry['timestamp'] == timestamp_iso:
            return True
    return False


LOCKFILE = "/tmp/count.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does

if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file

print("Creating lockfile")
Path(LOCKFILE).touch()

output_folder = "/home/pi/thesis/video_to_count"
json_folder = "/home/pi/thesis/json_all_measurements"
json_file = "measurements.json"
sensor_file_path = "/home/pi/thesis/json_sensor_only/sensors.json"

if not os.path.exists(json_folder):
    os.makedirs(json_folder)

json_path = os.path.join(json_folder, json_file)

data = []

if os.path.exists(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

for file_path in glob.glob(os.path.join(output_folder, '*.h264')):

    filename = os.path.basename(file_path)
    timestamp_str = os.path.splitext(filename)[0]
    timestamp_iso = convert_to_iso(timestamp_str)

    if not is_timestamp_present(data, timestamp_iso):

        vehicle_counter = VehicleCounter(file_path, "yolo_weights/yolov8n.pt", False, False)
        run_result = vehicle_counter.run()
        carCount, motorbikeCount, busCount, truckCount = run_result

        temperature = 0.0
        weather_category = ''
        air_quality = 0

        with open(sensor_file_path) as json_file:
            json_data = json.load(json_file)

            for item in json_data:
                if item['timestamp'] == timestamp_str:
                    temperature = item['temperature']
                    weather_category = item['weather_category']
                    air_quality = item['air_quality']
                    break
            json_file.close()

        print(f'{filename}')
        print(f'{"car:":<12}{carCount}')
        print(f'{"motorbike:":<12}{motorbikeCount}')
        print(f'{"truck:":<12}{truckCount}')
        print(f'{"bus:":<12}{busCount}')
        print(f'{"temperature:":<12}{temperature}')
        print(f'{"weather_category:":<12}{weather_category}')
        print(f'{"air_quality:":<12}{air_quality}')

        data.append({
            'timestamp': timestamp_iso,
            'carCount': carCount,
            'motorbikeCount': motorbikeCount,
            'busCount': busCount,
            'truckCount': truckCount,
            'temperature': temperature,
            'weather_category': weather_category,
            'air_quality': air_quality
        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()


# Remove the lock file
os.remove(LOCKFILE)
print("\nLockfile removed\n")
