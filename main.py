import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

# Initialize webcam

cap = cv2.VideoCapture("videos/motors2.h264")

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

# Initializing Sort tracker made by abewley

maxAge = 20
minHits = 3
iouThreshold = 0.3

carTracker = Sort(max_age=maxAge, min_hits=minHits, iou_threshold=iouThreshold)
motorbikeTracker = Sort(max_age=maxAge, min_hits=minHits, iou_threshold=iouThreshold)
busTracker = Sort(max_age=maxAge, min_hits=minHits, iou_threshold=iouThreshold)
truckTracker = Sort(max_age=maxAge, min_hits=minHits, iou_threshold=iouThreshold)

# Line positions

linePosition = [400, 0, 400, 480]
offset = 30
carCount = []
motorbikeCount = []
busCount = []
truckCount = []


def calculate_w_h(x_1, y_1, x_2, y_2):
    width = x_2 - x_1
    height = y_2 - y_1
    return width, height


def update_tracker(tracker, detections, count, type):
    tracker_results = tracker.update(detections)

    print(f'update tracker with {type}')

    for tracked_object in tracker_results:

        # Getting rect. data from the result

        t_x1, t_y1, t_x2, t_y2, tracking_id = tracked_object
        t_x1, t_y1, t_x2, t_y2, tracking_id = int(t_x1), int(t_y1), int(t_x2), int(t_y2), int(tracking_id)
        t_w, t_h = calculate_w_h(t_x1, t_y1, t_x2, t_y2)

        # Showing tracking bounding box, tracked object's id

        cvzone.cornerRect(img, (t_x1, t_y1, t_w, t_h), l=8, t=2, rt=1, colorR=(255, 0, 0))
        cvzone.putTextRect(img, f'[{tracking_id}] {type}',
                           (max(0, t_x1), max(30, t_y1)),
                           scale=0.8, thickness=1, offset=2, colorR=(0, 0, 102))
        print(f'tracking rect for {type}')

        # Center points

        t_cx, t_cy = t_x1 + t_w // 2, t_y1 + t_h // 2
        cv2.circle(img, (t_cx, t_cy), 3, (255, 0, 255), cv2.FILLED)

        # Increase the counter if the id has not been counted before

        if linePosition[0] - offset < t_cx < linePosition[0] + offset:
            if count.count(tracking_id) == 0:
                count.append(tracking_id)

    return count


while True:
    success, img = cap.read()
    results = model(img, stream=True)

    carDetections = np.empty((0, 5))
    motorbikeDetections = np.empty((0, 5))
    busDetections = np.empty((0, 5))
    truckDetections = np.empty((0, 5))

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

            # Defining the parameter for the sorting algorithm

            currentArray = np.array([x1, y1, x2, y2, conf])

            # If the conf. level is high enough, printing the conf. and class name
            # to the terminal and bounding box for selected classes

            if conf > 0.3:

                cvzone.cornerRect(img, bbox, l=8, t=2, rt=1)
                cvzone.putTextRect(img, f'{currentClass}',
                                   (max(0, x1), max(30, y1)),
                                   scale=0.8, thickness=1, offset=2)

                if currentClass == "car":
                    carDetections = np.vstack((carDetections, currentArray))
                    print("current class: car")
                    carCount = update_tracker(carTracker, carDetections, carCount, "car")

                if currentClass == "motorbike":
                    carDetections = np.vstack((motorbikeDetections, currentArray))
                    print("current class: motorbike")
                    motorbikeCount = update_tracker(motorbikeTracker, motorbikeDetections, motorbikeCount, "motorbike")

                if currentClass == "bus":
                    carDetections = np.vstack((busDetections, currentArray))
                    print("current class: bus")
                    busCount = update_tracker(busTracker, busDetections, busCount, "bus")

                if currentClass == "truck":
                    carDetections = np.vstack((truckDetections, currentArray))
                    print("current class: truck")
                    truckCount = update_tracker(truckTracker, truckDetections, truckCount, "truck")

    # Assigning tracking IDs to the detected objects






    # Drawing the lines

    cv2.line(img, (linePosition[0], linePosition[1]), (linePosition[2], linePosition[3]), (0, 0, 255), 2)
    cv2.line(img, (linePosition[0] - offset, linePosition[1]), (linePosition[2] - offset, linePosition[3]),
             (153, 153, 255), 1)
    cv2.line(img, (linePosition[0] + offset, linePosition[1]), (linePosition[2] + offset, linePosition[3]),
             (153, 153, 255), 1)

    # Displaying counters

    cvzone.putTextRect(img, f'car: {len(carCount)}', (20, 400), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'motorbike: {len(motorbikeCount)}', (20, 420), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'bus: {len(busCount)}', (20, 440), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'truck: {len(truckCount)}', (20, 460), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))

    cv2.imshow("Object counter", img)
    cv2.waitKey(0)
