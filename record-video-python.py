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

recording_length = 60 * 2

# Set the output directory

output_directory = "/home/pi/cam_output"

# Record videos splitted into parts

for i in range(4):

    # Set the output filename to the current timestamp

    output_filename = output_directory + time.strftime("%Y-%m-%d_%H-%M") + ".h264"

    camera.start_recording(output_filename)
    camera.wait_recording(recording_length)  # 1 minute = 60 seconds
    camera.stop_recording()

    time.sleep(2)

    print(f"Recorded {i+1} minutes of footage.")
    