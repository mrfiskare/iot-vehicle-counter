import os
import shutil

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Remove the content of the video backup folder
# day1_backup_path = "/home/pi/thesis/video_backup"
# if os.path.exists(day1_backup_path):
#     for root, dirs, files in os.walk(day1_backup_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             os.remove(file_path)
# else:
#     create_directory(day1_backup_path)

# Move all files from video count folder to the video backup folder
# output_path = "/home/pi/thesis/video_to_count"
# if os.path.exists(output_path):
#     for root, dirs, files in os.walk(output_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             os.remove(file_path)
# else:
#     create_directory(output_path)

# Delete the content of C:\videos\output
# if os.path.exists(output_path):
#     for root, dirs, files in os.walk(output_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             os.remove(file_path)


# Move all files from upload folder to the video count folder
input_path = "/home/pi/thesis/video_upload"
# output_path = "/home/pi/thesis/video_to_count"
output_path = "/media/pi/HDD/video_to_count"
if os.path.exists(input_path):
    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)
            shutil.move(file_path, output_path)
else:
    create_directory(input_path)
