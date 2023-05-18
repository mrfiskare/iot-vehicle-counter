#!C:/Users/pi/git/pte-yolo-node/venv/Scripts/python.exe

import os
import json
import glob
import shutil
import sys
import time
import datetime
from pathlib import Path

from pytz import timezone
from vehicle_counter import *
from weather import *


def count_vehicles(file_path):
    # Your implementation for counting vehicles goes here
    # Example implementation
    carCount = 5
    motorbikeCount = 3
    busCount = 2
    truckCount = 1

    return carCount, motorbikeCount, busCount, truckCount


def convert_to_iso(timestamp_str):
    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M")
    timestamp = timestamp.replace(tzinfo=timezone('Europe/Budapest'))
    return timestamp.isoformat()


def is_timestamp_present(data, timestamp_iso):
    for entry in data:
        if entry['timestamp'] == timestamp_iso:
            return True
    return False

LOCKFILE = "C:\\tmp\\count.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does

if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file

print("Creating lockfile")
Path(LOCKFILE).touch()

output_folder = "C:\\videos\\input"
json_folder = "C:\\videos\\final_json"
json_file = "measurements.json"
sensor_file_path = "C:\\videos\\sensor_json\\sensors.json"
video_backup_dir = "C:\\videos\\day1_backup\\"
prev_file = ""
filename = ""

if not os.path.exists(json_folder):
    os.makedirs(json_folder)

json_path = os.path.join(json_folder, json_file)

data = []

if os.path.exists(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

for file_path in glob.glob(os.path.join(output_folder, '*.h264')):

    if prev_file != "" and filename != "":
        os.rename(file_path, video_backup_dir + filename)

    filename = os.path.basename(file_path)
    timestamp_str = os.path.splitext(filename)[0]
    timestamp_iso = convert_to_iso(timestamp_str)

    if not is_timestamp_present(data, timestamp_iso):

        vehicle_counter = VehicleCounter(file_path, "yolo_weights\\yolov8n.pt", False, False)
        run_result = vehicle_counter.run()
        carCount, motorbikeCount, busCount, truckCount = run_result

        requestAPI = WeatherAPI(timestamp_iso)
        temperature = requestAPI.get_temperature()
        precipitation = requestAPI.get_precipitation()

        air_quality = 0
        carbon_monoxide = 0

        with open(sensor_file_path) as json_file:
            json_data = json.load(json_file)

            for item in json_data:
                if item['timestamp'] == timestamp_str:
                    air_quality = item['air_quality']
                    carbon_monoxide = item['carbon_monoxide']
                    break

        print(f'{filename}')
        print(f'{"car:":<12}{carCount}')
        print(f'{"motorbike:":<12}{motorbikeCount}')
        print(f'{"truck:":<12}{truckCount}')
        print(f'{"bus:":<12}{busCount}')
        print(f'{"temperature:":<12}{temperature}')
        print(f'{"precipitation:":<12}{precipitation}')
        print(f'{"air_quality:":<12}{air_quality}')
        print(f'{"carbon_monoxide:":<12}{carbon_monoxide}')

        data.append({
            'timestamp': timestamp_iso,
            'carCount': carCount,
            'motorbikeCount': motorbikeCount,
            'busCount': busCount,
            'truckCount': truckCount,
            'temperature': temperature,
            'precipitation': precipitation,
            'air_quality': air_quality,
            'carbon_monoxide': carbon_monoxide,

        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()


# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")
