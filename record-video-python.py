import picamera

with picamera.PiCamera() as camera:

    camera.resolution = (640, 640)
    camera.vflip = True
    time.sleep(2)
    camera.capture("/home/pi/Pictures/img.jpg")
    print("Done.")
