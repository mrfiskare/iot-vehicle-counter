from ultralytics import YOLO
import cv2
import cvzone
import math

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

model = YOLO("../yolo_weights/yolov8n.pt")

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    for r in results:

        # Drawing bounding boxes around objects with cvzone

        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3) # pure opencv rectangle
            w, h = x2-x1, y2-y1
            bbox = x1, y1, w, h
            cvzone.cornerRect(img, bbox)

            # Rounding confidence to 2 decimals and printing it on the bounding box

            conf = math.ceil(box.conf[0]*100)/100
            print(conf)
            cvzone.putTextRect(img, f'{conf}', (max(0, x1), max(30, y1)))


    cv2.imshow("Image", img)
    cv2.waitKey(1)
