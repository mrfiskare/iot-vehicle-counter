#!/bin/bash

# Stop running in case of failure

set -e

# Reset BASH time counter

SECONDS=0

# Export every 20th frame (every 2nd sec) from the video

for file in /home/pi/recording/recorded/*.h264
do
    ffmpeg -i "$file" -vf "select=not(mod(n\,20))" -vsync vfr "${file%.*}"_%05d.jpg
    rm -rf "$file"
done

ELAPSED="Elapsed: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"