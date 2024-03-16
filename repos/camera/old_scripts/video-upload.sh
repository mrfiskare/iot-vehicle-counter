#!/bin/bash

# Stop running in case of failure

set -e

# Set variables

AZ_STORAGE_ACCOUNT="$1"
AZ_STORAGE_ACCESS_KEY="$2"
CONTAINER_NAME="$3"
LOCAL_DIR="/home/pi/recording/recorded"
LOCK_FILE="/tmp/upload.lock"

# Check if another instance of the script is running

if [ -f "$LOCK_FILE" ]; then
  echo "Another instance of the script is running, exiting."
  exit 1
fi

# Create a lock file to prevent another instance of the script from running

touch $LOCK_FILE

# Upload new files to Azure Blob storage

az storage blob upload-batch --account-name $AZ_STORAGE_ACCOUNT --account-key $AZ_STORAGE_ACCESS_KEY --destination $CONTAINER_NAME --source $LOCAL_DIR --pattern "*"

# Delete uploaded files

if [ $? -eq 0 ]; then
  rm -rf $LOCAL_DIR/*
fi

# Remove lock file
rm $LOCK_FILE