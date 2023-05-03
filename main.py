import os
import json
import glob
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

output_folder = "C:/videos/output"
# output_folder = "C:\\Users\\pi\\git\\pte-yolo-node\\videos"
json_folder = "C:/videos/unprocessed_json"
json_file = "measurements.json"

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

    vehicle_counter = VehicleCounter(file_path, "yolo_weights/yolov8n.pt", False, False)

    run_result = vehicle_counter.run()
    carCount, motorbikeCount, busCount, truckCount = run_result

    print(f'{filename}')
    print(f'{"car:":<12}{carCount}')
    print(f'{"motorbike:":<12}{motorbikeCount}')
    print(f'{"truck:":<12}{truckCount}')
    print(f'{"bus:":<12}{busCount}\n')

    data.append({
        'timestamp': timestamp_iso,
        'carCount': carCount,
        'motorbikeCount': motorbikeCount,
        'busCount': busCount,
        'truckCount': truckCount
    })

with open(json_path, 'w') as file:
    json.dump(data, file, indent=4)
