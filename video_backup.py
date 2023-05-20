import os
import shutil

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Remove the content of C:\videos\day1_backup
day1_backup_path = r'C:\videos\day1_backup'
if os.path.exists(day1_backup_path):
    for root, dirs, files in os.walk(day1_backup_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
else:
    create_directory(day1_backup_path)

# Move all files from C:\videos\output to C:\videos\day1_backup
output_path = r'C:\videos\output'
day1_backup_path = r'C:\videos\day1_backup'
if os.path.exists(output_path):
    for root, dirs, files in os.walk(output_path):
        for file in files:
            file_path = os.path.join(root, file)
            shutil.move(file_path, day1_backup_path)
else:
    create_directory(output_path)

# Delete the content of C:\videos\output
if os.path.exists(output_path):
    for root, dirs, files in os.walk(output_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

# Move all files from C:\videos\input to C:\videos\output
input_path = r'C:\videos\input'
output_path = r'C:\videos\output'
if os.path.exists(input_path):
    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)
            shutil.move(file_path, output_path)
else:
    create_directory(input_path)
