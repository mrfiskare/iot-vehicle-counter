#!/usr/bin/env python3

import os
import sys
import glob
import subprocess
from pathlib import Path

LOCKFILE = "/tmp/upload_videos_scp.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does
if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file
print("Creating lockfile")
Path(LOCKFILE).touch()

SOURCE_DIR = "/home/pi/recording/recorded/"
DEST_DIR = "C:/videos/input"

if len(sys.argv) < 5:
    print("Usage: script.py <WINDOWS_SERVER_IP> <SSH_PORT> <SSH_USER> <PASSWORD>")
    sys.exit(1)

WINDOWS_SERVER_IP = sys.argv[1]
SSH_PORT = sys.argv[2]
SSH_USER = sys.argv[3]
PASSWORD = sys.argv[4]

# Find .h264 video files and upload them to the Windows Server
for file in glob.glob(SOURCE_DIR + "**/*.h264", recursive=True):
    print(f"Uploading {file} to {WINDOWS_SERVER_IP}:{DEST_DIR}")

    result = subprocess.run(
        [
            "sshpass",
            "-p",
            PASSWORD,
            "scp",
            "-P",
            SSH_PORT,
            "-o",
            "StrictHostKeyChecking=no",
            file,
            f"{SSH_USER}@{WINDOWS_SERVER_IP}:{DEST_DIR}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode == 0:
        print(f"Upload successful: {file}")
        os.remove(file)
    else:
        print(f"Error uploading: {file}")


print("Cropping videos on Windows Server")
command = f"sshpass -p {PASSWORD} ssh -p 22 pi@{WINDOWS_SERVER_IP} 'python C:/scripts/video-crop.py'"
    
try:
    subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    print("Video cropping completed successfully.")

except subprocess.CalledProcessError as e:
    print(f"Error occurred during video cropping: {e.output.decode('utf-8')}")


# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")
