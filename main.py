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
from arduino_reader import *


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

output_folder = "C:\\videos\\output"
json_folder = "C:\\videos\\unprocessed_json"
json_file = "measurements.json"
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

        # Get the temp and precipitation from open API
        requestAPI = WeatherAPI(timestamp_iso)
        temperature = requestAPI.get_temperature()
        precipitation = requestAPI.get_precipitation()

        # Set the arduino port and baud rate
        arduino = ArduinoReader('/dev/ttyACM0', 9600)

        # Get the sensor values
        measurement_id = arduino.get_measurement_id()
        mq7_value = arduino.get_co2_sensor()
        mq135_value = arduino.get_air_quality_sensor()

        print(f'{filename}')
        print(f'{"car:":<12}{carCount}')
        print(f'{"motorbike:":<12}{motorbikeCount}')
        print(f'{"truck:":<12}{truckCount}')
        print(f'{"bus:":<12}{busCount}')
        print(f'{"temperature:":<12}{truckCount}')
        print(f'{"precipitation:":<12}{busCount}')
        print(f'{"air_quality_sensor:":<12}{truckCount}')
        print(f'{"co2_sensor:":<12}{busCount}')

        data.append({
            'timestamp': timestamp_iso,
            'carCount': carCount,
            'motorbikeCount': motorbikeCount,
            'busCount': busCount,
            'truckCount': truckCount,
            'temperature': temperature,
            'precipitation': precipitation,
            'air_quality_sensor': temperature,
            'co2_sensor': precipitation,

        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()

# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")
