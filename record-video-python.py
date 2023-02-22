import time
import picamera

# Set up the PiCamera object

camera = picamera.PiCamera()
camera.resolution = (640, 640)
camera.vflip = True
camera.hflip = True
camera.zoom=(0.3,0.3,0.7,0.7)
camera.framerate = 15

# Set the recording length (in seconds)

recording_length = 60

# Set the total recording time (in seconds)

total_recording_time = 8 * 60

# Set the output directory

output_directory = "/home/pi/"

# Record 4 1-minute long videos

file_name = output_directory + 'video_{:02d}.h264'

for i in range(4):

    camera.start_recording(file_name.format(i))
    camera.wait_recording(60)  # 1 minute = 60 seconds
    camera.stop_recording()
    