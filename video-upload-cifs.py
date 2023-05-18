#!/usr/bin/env python3

import os
import sys
import glob
import subprocess
from pathlib import Path

LOCKFILE = "/tmp/upload_videos_cifs.lock"

print("Checking lockfile...")

# Check if the lock file exists, exit if it does
if os.path.exists(LOCKFILE):
    print("Another instance of the script is already running. Exiting.")
    sys.exit(1)

# Create the lock file
print("Creating lockfile")
Path(LOCKFILE).touch()

SOURCE_DIR = "/home/pi/recording/recorded/"
DEST_DIR = "/home/pi/windows-share/"

# Get all files in the source_dir
try:
    files = glob.glob(SOURCE_DIR + "*")  

except Exception as e:
    print(f"Error occurred while trying to access source directory: {str(e)}")
    files = []

for file in files:
    try:
        shutil.move(file, DEST_DIR)

    except Exception as e:
        print(f"Error occurred while moving file {file}: {str(e)}")

# Remove the lock file
os.remove(LOCKFILE)
print("Lockfile removed\n")
