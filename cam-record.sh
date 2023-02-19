#!/bin/bash

# Stop running in case of failure

set -e

# Get the current date and time

date=$(date +%F_%H-%M)

# Set directory for video files

cam_output="/home/pi/cam_output/"
mkdir -p "$cam_output"

# Set the name of the video files

file_name="recording.h264"
path="$cam_output""$file_name"

# Record raw video

raspivid \
    --width 640 \
    --height 640 \
    --timeout 240000 \
    --rotation 180 \
    --framerate 15 \
    --roi 0.3,0.3,0.6,0.6 \
    --output "$path"
