import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

# Initialize webcam

cap = cv2.VideoCapture("videos/7_cars.h264")

# Initialize YOLO

model = YOLO("yolo_weights/yolov8n.pt")
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus",
              "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign",
              "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
              "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag",
              "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
              "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
              "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
              "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
              "donut", "cake", "chair", "sofa", "pottedplant", "bed", "diningtable",
              "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock",
              "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
vehicleTypes = ["car", "motorbike", "bus", "truck"]

# Initializing Sort tracker made by abewley

tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)


def calculate_w_h(x_1, y_1, x_2, y_2):
    width = x_2 - x_1
    height = y_2 - y_1
    return width, height


while True:
    success, img = cap.read()
    results = model(img, stream=True)
    detections = np.empty((0, 5))

    for r in results:

        # Drawing bounding boxes around specified objects with cvzone

        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = calculate_w_h(x1, y1, x2, y2)
            bbox = x1, y1, w, h

            # Rounding confidence to 2 decimals

            conf = math.ceil(box.conf[0] * 100) / 100

            # Getting the class name, using the pre-defined array of coco-classes

            cls = int(box.cls[0])
            currentClass = classNames[cls]

            # If the conf. level is high enough, printing the conf. and class name
            # to the terminal and bounding box for selected classes

            if conf > 0.3:

                if currentClass in vehicleTypes:

                    # Showing detection bounding box, conf. and class name (commented out)

                    cvzone.cornerRect(img, bbox, l=8, t=2, rt=1)
                    # cvzone.putTextRect(img, f'{currentClass} {conf}',
                    #                    (max(0, x1), max(30, y1)),
                    #                    scale=0.8, thickness=1, offset=2)
                    # print(f'class: {currentClass} {conf}')

                    # Adding the detected objects to the detections array

                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

    # Assigning tracking IDs to the detected objects

    resultsTracker = tracker.update(detections)
    for results in resultsTracker:

        # Getting rect. data from the result

        t_x1, t_y1, t_x2, t_y2, tracking_id = results
        t_x1, t_y1, t_x2, t_y2, tracking_id = int(t_x1), int(t_y1), int(t_x2), int(t_y2), int(tracking_id)
        t_w, t_h = calculate_w_h(t_x1, t_y1, t_x2, t_y2)

        # Showing tracking bounding box, tracked object's id

        cvzone.cornerRect(img, (t_x1, t_y1, t_w, t_h), l=8, t=2, rt=1, colorR=(255, 0, 0))
        cvzone.putTextRect(img, f'{tracking_id}',
                           (max(0, t_x1), max(30, t_y1)),
                           scale=0.8, thickness=1, offset=2)

    cv2.imshow("Object counter", img)
    cv2.waitKey(1)
