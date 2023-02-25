import sys
import time
import subprocess
import picamera
import os
import psutil
import shutil

# Unload the bcm2835-v4l2 driver

subprocess.run(["sudo", "modprobe", "-r", "bcm2835-v4l2"])
time.sleep(2)
subprocess.run(["sudo", "modprobe", "bcm2835-v4l2"])
time.sleep(2)

# Set up the PiCamera object

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.vflip = True
camera.hflip = True
camera.zoom=(0.3,0.4,0.65,0.45)
camera.framerate = 10

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

for i in range(1):

    # Get the available space on the root partition in GB

    available_space = psutil.disk_usage('/').free
    available_space_gb = available_space / (1024 ** 3)
    print(f"\nAvailable space: {available_space_gb:.2f} GB", file=sys.stdout, flush=True)

    # Check if available space is at least 10 GB

    if available_space_gb < 10:

        sys.exit("Error: Not enough free space on the machine!")

    else:

    # Set the output filename to the current timestamp

        timestamped_file = time.strftime("%Y-%m-%d_%H-%M") + ".h264"
        output_filename = output_directory + timestamped_file

        camera.start_recording(output_filename)
        camera.wait_recording(recording_length)
        camera.stop_recording()
        time.sleep(2)
        
        # Move the file to the captured folder

        os.rename(output_filename, done_directory + timestamped_file)
        print(f"Recorded: {done_directory}{timestamped_file}", file=sys.stdout, flush=True)

camera.close()
time.sleep(5)
print("\n")