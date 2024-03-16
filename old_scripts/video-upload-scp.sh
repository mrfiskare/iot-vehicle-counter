#!/bin/bash

LOCKFILE="/tmp/upload_videos.lock"

# Check if the lock file exists, exit if it does

if [ -e "${LOCKFILE}" ]; then
    echo "Another instance of the script is already running. Exiting."
    exit 1
fi

# Create the lock file

touch "${LOCKFILE}"

SOURCE_DIR="/home/pi/recording/recorded/"
DEST_DIR="C:/videos/input"
WINDOWS_SERVER_IP="$1"
SSH_PORT="$2"
SSH_USER="$3"
PASSWORD="$4"

# Find .h264 video files and upload them to the Windows Server

find "${SOURCE_DIR}" -type f -iname "*.h264" | while read -r file
do
    echo "Uploading ${file} to ${WINDOWS_SERVER_IP}:${DEST_DIR}"
    sshpass -p "${PASSWORD}" scp -P "${SSH_PORT}" -o StrictHostKeyChecking=no "${file}" "${SSH_USER}@${WINDOWS_SERVER_IP}:${DEST_DIR}"
    if [ $? -eq 0 ]; then
        echo "Upload successful: ${file}"
    else
        echo "Error uploading: ${file}"
    fi
done

# Remove the lock file

rm "${LOCKFILE}"

