import os
import sys
import subprocess
import time
from pathlib import Path

LOCKFILE = "C:\\videos\\crop_videos.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does

if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file

print("Creating lockfile")
Path(LOCKFILE).touch()

input_directory = "C:\\videos\\input\\"
crop_tmp_directory = "C:\\videos\\crop_tmp_directory\\"
output_directory = "C:\\videos\\output\\"
timestamp = ""
output_filename = ""

# Make sure the output and done directories exist

os.makedirs(crop_tmp_directory, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

# Iterate over all files in the input directory

for filename in os.listdir(input_directory):

    # Check if the file is an h264 video

    if filename.endswith(".h264"):

        # Moving finished file

        if timestamp != "" and output_filename != "":
            final_filename = output_directory + timestamp + ".h264"
            os.rename(output_filename, final_filename)
        
        input_file = os.path.join(input_directory, filename)
        timestamp = filename[:-4]
        
        # Cropping the video to 720p

        print("cropping video ...")

        # Lossy H264 conversion

        output_filename = crop_tmp_directory + timestamp + ".h264"

        ffmpeg_command = [
            "ffmpeg",
            "-i", input_file,
            "-vf", "crop=1280:720:640:360",
            "-c:v", "libx264",
            "-crf", "18",  # Increase this value for a smaller file size (e.g., 25 or 28) and lower quality
            "-preset", "medium",  # Use 'fast' or 'faster' for a faster encoding with a slightly larger file size
            "-an",
            "-r", "30",
            output_filename
        ]

        result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:

            print(f"Successfully processed {input_file} and saved it as {final_filename}", file=sys.stdout, flush=True)

            # Delete the input file

            try:
                os.remove(input_file)
                print(f"Deleted the input file: {input_file}")

            except OSError as e:
                print(f"Error deleting the input file: {e}")

        else:
            
            print(f"An error occurred while processing {input_file}")
            print(f"Error details: {result.stderr.decode('utf-8')}")


# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")
