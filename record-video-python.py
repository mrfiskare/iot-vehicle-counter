from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (640, 640)
camera.vflip = True
camera.hflip = True
camera.zoom=(0.3,0.3,0.7,0.7)
camera.framerate = 15

# Record 4 1-minute long videos
file_name = '/home/pi/video_{:02d}.h264'
for i in range(4):
    camera.start_recording(file_name.format(i))
    camera.wait_recording(60)  # 1 minute = 60 seconds
    camera.stop_recording()
    