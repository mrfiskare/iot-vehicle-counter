import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *


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


def calculate_w_h(x_1, y_1, x_2, y_2):
    width = x_2 - x_1
    height = y_2 - y_1
    return width, height


def sort_array(np_array):
    sorted_np_array = np.argsort(np_array[:, 0])
    return np_array[sorted_np_array]


class VehicleCounter:

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

    def update_tracker(self, tracker, detections, img):

        # Matching the rows from detections to tracker_results.
        # This is needed because the detections array contains the vehicle types,
        # whereas the tracker_results array contains the tracking ids.

        tracker_results = tracker.update(detections)
        tracker_results = match_array_tuples(detections, tracker_results)

        for tracked_object in tracker_results:

            # Getting coordinates, id, type data from tracker_results

            t_x1, t_y1, t_x2, t_y2, tracking_id, type_index = tracked_object
            t_w, t_h = calculate_w_h(t_x1, t_y1, t_x2, t_y2)
            cls_name = self.classNames[type_index]

            # Showing tracking bounding box, tracked object's id

            # Center points

            t_cx, t_cy = t_x1 + t_w // 2, t_y1 + t_h // 2
            cv2.circle(img, (t_cx, t_cy), 3, (255, 0, 255), cv2.FILLED)

            # Increase the counter if the id has not been counted before

            if self.linePosition[0] - self.offset < t_cx < self.linePosition[0] + self.offset:

                if cls_name == "car" and self.carCount.count(tracking_id) == 0:
                    self.carCount.append(tracking_id)

                if cls_name == "motorbike" and self.motorbikeCount.count(tracking_id) == 0:
                    self.motorbikeCount.append(tracking_id)

                if cls_name == "truck" and self.truckCount.count(tracking_id) == 0:
                    self.truckCount.append(tracking_id)

                if cls_name == "bus" and self.busCount.count(tracking_id) == 0:
                    self.busCount.append(tracking_id)

    def count(self, file_path):

        # Initialize video

        cap = cv2.VideoCapture(file_path)

        while True:
            success, img = cap.read()
            results = self.model(img, stream=True)
            yolo_detections = np.empty((0, 6))

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
                    current_class = self.classNames[cls]

                    # Defining the parameter for the sorting algorithm

                    current_array = np.array([x1, y1, x2, y2, conf, cls])

                    # If the conf. level is high enough, printing the conf. and class name
                    # to the terminal and bounding box for selected classes

                    if conf > 0.2:

                        if current_class in self.vehicleTypes:
                            yolo_detections = np.vstack((yolo_detections, current_array))

            # Assigning tracking IDs to the detected objects

            self.update_tracker(self.vehicleTracker, yolo_detections, img)
            print("track")
            cv2.waitKey(0)

        return len(self.carCount), len(self.motorbikeCount), len(self.busCount), len(self.truckCount)



