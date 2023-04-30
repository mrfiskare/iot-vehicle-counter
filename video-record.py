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
camera.resolution = (1920, 1080)
camera.vflip = True
camera.hflip = True
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

        # Cropping the video to 720p

        print("cropping video ...")
        input_file = output_filename
        output_file = output_directory + timestamp + ".mkv"

        # Define the FFmpeg command

        ffmpeg_command = [
            "ffmpeg",
            "-i", input_file,
            "-vf", "crop=1280:720:640:360",
            "-c:v", "ffv1",
            "-an",
            "-r", "10",
            output_file
        ]

        # Run the FFmpeg command using subprocess

        result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the FFmpeg command was successful

        if result.returncode == 0:

            print(f"Successfully processed {input_file} and saved it as {output_file}")
            
            # Move the file to the captured folder

            os.rename(output_file, done_directory + timestamp + ".mkv")
            print(f"Recorded: {done_directory}{timestamp}.mkv", file=sys.stdout, flush=True)

            # Delete the input file

            try:
                os.remove(input_file)
                print(f"Deleted the input file: {input_file}")

            except OSError as e:
                print(f"Error deleting the input file: {e}")

        else:
            print(f"An error occurred while processing {input_file}")
            print(f"Error details: {result.stderr.decode('utf-8')}")

camera.close()
time.sleep(5)
print("\n")
