import picamera
import time

with picamera.PiCamera() as camera:

    camera.resolution = (640, 640)
    camera.vflip = True
    time.sleep(2)
    camera.capture("/home/pi/img.jpg")
    print("Done.")
