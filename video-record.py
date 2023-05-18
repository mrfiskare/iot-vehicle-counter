import sys
import time
import subprocess
import picamera
import os
import psutil
import shutil
from pathlib import Path
from ArduinoReader import *

# Unload the bcm2835-v4l2 driver

subprocess.run(["sudo", "modprobe", "-r", "bcm2835-v4l2"])
time.sleep(2)
subprocess.run(["sudo", "modprobe", "bcm2835-v4l2"])
time.sleep(2)

LOCKFILE = "/tmp/record_videos.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does
if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file
print("Creating lockfile")
Path(LOCKFILE).touch()

# Set up the PiCamera object

camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.vflip = True
camera.hflip = True
camera.framerate = 30

# Set the recording length (in seconds)

recording_length = 60 * 60

# Set the output directories

output_directory = "/home/pi/recording/"
done_directory = "/home/pi/recording/recorded/"

# Delete previous recordings

if os.path.exists(output_directory) :
    shutil.rmtree(output_directory)

if not os.path.exists(output_directory) :
    os.makedirs(output_directory)

if os.path.exists(done_directory) :
    shutil.rmtree(done_directory)

if not os.path.exists(done_directory) :
    os.makedirs(done_directory)

# Record videos splitted into parts

for i in range(8):

    # Get the available space on the root partition in GB

    available_space = psutil.disk_usage('/').free
    available_space_gb = available_space / (1024 ** 3)
    print(f"\nAvailable space: {available_space_gb:.2f} GB", file=sys.stdout, flush=True)

    # Check if available space is at least 5 GB

    if available_space_gb < 5:

        sys.exit("Error: Not enough free space on the machine!")

    else:

        # Set the output filename to the current timestamp

        timestamp = time.strftime("%Y-%m-%d_%H-%M")
        timestamped_file = timestamp + ".h264"
        output_filename = output_directory + timestamped_file

        camera.start_recording(output_filename)
        camera.wait_recording(recording_length)
        camera.stop_recording()
        time.sleep(2)

        # Read Arduino values

        arduino = ArduinoReader('/dev/ttyACM0', 9600)
        arduino.save_to_file(arduino.read_from_arduino(timestamp))

        # Move the file to the captured folder

        os.rename(output_filename, done_directory + timestamped_file)
        print(f"Recorded: {done_directory}{timestamp}.h264", file=sys.stdout, flush=True)


camera.close()
time.sleep(5)

# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")