import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

# Initialize webcam

cap = cv2.VideoCapture("videos/1.h264")
showImg = True

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

maxAge = 20
minHits = 3
iouThreshold = 0.3

vehicleTracker = Sort(max_age=maxAge, min_hits=minHits, iou_threshold=iouThreshold)

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


def sort_array(np_array):
    sorted_np_array = np.argsort(np_array[:, 0])
    return np_array[sorted_np_array]


def match_array_tuples(detections_arr, tracking_arr):
    # The resulting array with [x1, y1, x2, y2, id, type]

    arr_with_id_and_type = np.empty((0, 6))

    # Removing unnecessary values for matching

    detections_arr_coordinates_only = detections_arr[:, :-2]
    tracking_arr_coordinates_only = tracking_arr[:, :-1]

    for index, arr_tuple in enumerate(tracking_arr_coordinates_only):

        # Compute the Euclidean distances

        distances = np.linalg.norm(detections_arr_coordinates_only - arr_tuple, axis=1)

        # Find the index of the minimum distance

        min_distance_index = np.argmin(distances)

        # Get the closest row
        # closest_row = detections_arr[min_distance_index]

        # Generate the resulting row with coordinates, tracking id and vehicle type id

        result = np.array([
            [tracking_arr[index, 0],
             tracking_arr[index, 1],
             tracking_arr[index, 2],
             tracking_arr[index, 3],
             tracking_arr[index, 4],
             detections_arr[min_distance_index, 5]]
        ])

        arr_with_id_and_type = np.vstack([arr_with_id_and_type, result])

    return arr_with_id_and_type.astype(int)


def update_tracker(tracker, detections):

    # Matching the rows from detections to tracker_results.
    # This is needed because the detections array contains the vehicle types,
    # whereas the tracker_results array contains the tracking ids.

    tracker_results = tracker.update(detections)
    tracker_results = match_array_tuples(detections, tracker_results)

    for tracked_object in tracker_results:

        # Getting coordinates, id, type data from tracker_results

        t_x1, t_y1, t_x2, t_y2, tracking_id, type_index = tracked_object
        t_w, t_h = calculate_w_h(t_x1, t_y1, t_x2, t_y2)
        cls_name = classNames[type_index]

        # Showing tracking bounding box, tracked object's id

        if showImg:
            cvzone.cornerRect(img, (t_x1, t_y1, t_w, t_h), l=8, t=2, rt=1, colorR=(255, 0, 0))
            cvzone.putTextRect(img, f'[{tracking_id}] {cls_name}',
                               (max(0, t_x1), max(30, t_y1)),
                               scale=0.8, thickness=1, offset=2, colorR=(0, 0, 102))

        # Center points

        t_cx, t_cy = t_x1 + t_w // 2, t_y1 + t_h // 2
        cv2.circle(img, (t_cx, t_cy), 3, (255, 0, 255), cv2.FILLED)

        # Increase the counter if the id has not been counted before

        if linePosition[0] - offset < t_cx < linePosition[0] + offset:

            if cls_name == "car" and carCount.count(tracking_id) == 0:
                carCount.append(tracking_id)

            if cls_name == "motorbike" and motorbikeCount.count(tracking_id) == 0:
                motorbikeCount.append(tracking_id)

            if cls_name == "truck" and truckCount.count(tracking_id) == 0:
                truckCount.append(tracking_id)

            if cls_name == "bus" and busCount.count(tracking_id) == 0:
                busCount.append(tracking_id)


while True:
    success, img = cap.read()
    results = model(img, stream=True)

    yoloDetections = np.empty((0, 6))

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

            currentArray = np.array([x1, y1, x2, y2, conf, cls])

            # If the conf. level is high enough, printing the conf. and class name
            # to the terminal and bounding box for selected classes

            if conf > 0.2:

                # if showImg:
                #     cvzone.cornerRect(img, bbox, l=8, t=2, rt=1)
                #     cvzone.putTextRect(img, f'{currentClass}',
                #                        (max(0, x1), max(30, y1)),
                #                        scale=0.8, thickness=1, offset=2)

                if currentClass in vehicleTypes:
                    yoloDetections = np.vstack((yoloDetections, currentArray))

    # Assigning tracking IDs to the detected objects

    update_tracker(vehicleTracker, yoloDetections)

    # Drawing the lines

    if showImg:
        cv2.line(img, (linePosition[0], linePosition[1]), (linePosition[2], linePosition[3]), (0, 0, 255), 2)
        cv2.line(img, (linePosition[0] - offset, linePosition[1]), (linePosition[2] - offset, linePosition[3]),
                 (153, 153, 255), 1)
        cv2.line(img, (linePosition[0] + offset, linePosition[1]), (linePosition[2] + offset, linePosition[3]),
                 (153, 153, 255), 1)

    # Displaying counters

    if showImg:
        cvzone.putTextRect(img, f'{"car:":<13}{len(carCount)}', (20, 400), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))
        cvzone.putTextRect(img, f'{"motorbike:":<12}{len(motorbikeCount)}', (20, 420), scale=1.2, thickness=1, offset=2,
                           colorR=(0, 0, 0))
        cvzone.putTextRect(img, f'{"truck:":<13}{len(truckCount)}', (20, 440), scale=1.2, thickness=1, offset=2, colorR=(0, 0, 0))
        cvzone.putTextRect(img, f'{"bus:":<13}{len(busCount)}', (20, 460), scale=1.2, thickness=1, offset=2,
                           colorR=(0, 0, 0))

    print(f'{"car:":<12}{len(carCount)}')
    print(f'{"motorbike:":<12}{len(motorbikeCount)}')
    print(f'{"truck:":<12}{len(truckCount)}')
    print(f'{"bus:":<12}{len(busCount)}')

    if showImg:
        cv2.imshow("Vehicle counter", img)
    cv2.waitKey(1)
