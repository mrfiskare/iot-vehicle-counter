#!/bin/bash

# Stop running in case of failure
set -e

path="/home/pi/cam_output/"
datetime=$(date +%s)
name="part"
ext=".txt"

# Incrementing video part names by 1 hour

for n in 1 2 3 4 5 6 7 8
do
    datetime=$((datetime + 3600))
    cp "$path""$name""$n""$ext" "$path""$(date -d "@$datetime" +"%Y-%m-%d_%H-%M")""$ext"
done
