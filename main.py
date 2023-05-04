#!C:/Users/pi/git/pte-yolo-node/venv/Scripts/python.exe

import os
import json
import glob
import shutil
import time
import datetime
from pytz import timezone
from vehicle_counter import *


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


output_folder = "C:\\videos\\output"
json_folder = "C:\\videos\\unprocessed_json"
json_file = "measurements.json"
video_backup_dir = "C:\\videos\\day1_backup\\"

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

        vehicle_counter = VehicleCounter(file_path, "yolo_weights\\yolov8n.pt", False, False)

        run_result = vehicle_counter.run()
        carCount, motorbikeCount, busCount, truckCount = run_result

        print(f'{filename}')
        print(f'{"car:":<12}{carCount}')
        print(f'{"motorbike:":<12}{motorbikeCount}')
        print(f'{"truck:":<12}{truckCount}')
        print(f'{"bus:":<12}{busCount}')

        data.append({
            'timestamp': timestamp_iso,
            'carCount': carCount,
            'motorbikeCount': motorbikeCount,
            'busCount': busCount,
            'truckCount': truckCount
        })

        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)
            file.close()

        os.rename(file_path, video_backup_dir + filename)
