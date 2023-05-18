import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *


class VehicleCounter:
    def __init__(self, video_path="videos/10s_1080p.h264", yolo_weights_path="yolo_weights/yolov8n.pt", show_img=True, verbose=True):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.show_img = show_img
        self.verbose = verbose

        # Initialize YOLO
        self.model = YOLO(yolo_weights_path)
        self.classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus",
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
        self.vehicleTypes = ["car", "motorbike", "bus", "truck"]

        self.mask = cv2.imread("mask.png")

        # Initializing Sort tracker made by abewley
        max_age = 20
        min_hits = 3
        iou_threshold = 0.3

        self.vehicleTracker = Sort(max_age=max_age, min_hits=min_hits, iou_threshold=iou_threshold)

        # Line positions
        self.linePosition = [1460, 399, 1460, 1080]
        self.offset = 30
        self.carCount = []
        self.motorbikeCount = []
        self.busCount = []
        self.truckCount = []

    @staticmethod
    def calculate_w_h(x_1, y_1, x_2, y_2):
        width = x_2 - x_1
        height = y_2 - y_1
        return width, height

    @staticmethod
    def sort_array(np_array):
        sorted_np_array = np.argsort(np_array[:, 0])
        return np_array[sorted_np_array]

    @staticmethod
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

    def update_tracker(self, tracker, detections, img):
        # Matching the rows from detections to tracker_results.
        # This is needed because the detections array contains the vehicle types,
        # whereas the tracker_results array contains the tracking ids.

        tracker_results = tracker.update(detections)
        tracker_results = self.match_array_tuples(detections, tracker_results)

        for tracked_object in tracker_results:
            # Getting coordinates, id, type data from tracker_results
            t_x1, t_y1, t_x2, t_y2, tracking_id, type_index = tracked_object
            t_w, t_h = self.calculate_w_h(t_x1, t_y1, t_x2, t_y2)
            cls_name = self.classNames[type_index]

            # Showing tracking bounding box, tracked object's id
            if self.show_img:
                cvzone.cornerRect(img, (t_x1, t_y1, t_w, t_h), l=8, t=3, rt=2, colorR=(255, 0, 0))
                cvzone.putTextRect(img, f'[{tracking_id}] {cls_name}',
                                   (max(0, t_x1), max(30, t_y1)),
                                   scale=1.4, thickness=2, offset=2, colorR=(0, 0, 102))

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

    def run(self):
        while True:
            ret, im = self.cap.read()
            img_region = cv2.bitwise_and(im, self.mask)
            results = self.model(img_region, stream=True)

            if not ret or im is None:
                if self.verbose:
                    print("Error: Unable to read frame. Exiting...")
                break

            yoloDetections = np.empty((0, 6))

            for r in results:
                # Drawing bounding boxes around specified objects with cvzone
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = self.calculate_w_h(x1, y1, x2, y2)
                    bbox = x1, y1, w, h

                    # Rounding confidence to 2 decimals
                    conf = math.ceil(box.conf[0] * 100) / 100

                    # Getting the class name, using the pre-defined array of coco-classes
                    cls = int(box.cls[0])
                    currentClass = self.classNames[cls]

                    # Defining the parameter for the sorting algorithm
                    currentArray = np.array([x1, y1, x2, y2, conf, cls])

                    # If the conf. level is high enough, printing the conf. and class name
                    # to the terminal and bounding box for selected classes
                    if conf > 0.2:

                        if currentClass in self.vehicleTypes:
                            yoloDetections = np.vstack((yoloDetections, currentArray))

                # Assigning tracking IDs to the detected objects
                self.update_tracker(self.vehicleTracker, yoloDetections, img_region)

                # Drawing the lines
                if self.show_img:
                    cv2.line(img_region, (self.linePosition[0], self.linePosition[1]),
                             (self.linePosition[2], self.linePosition[3]), (0, 0, 255), 2)
                    cv2.line(img_region, (self.linePosition[0] - self.offset, self.linePosition[1]),
                             (self.linePosition[2] - self.offset, self.linePosition[3]),
                             (153, 153, 255), 1)
                    cv2.line(img_region, (self.linePosition[0] + self.offset, self.linePosition[1]),
                             (self.linePosition[2] + self.offset, self.linePosition[3]),
                             (153, 153, 255), 1)

                # Displaying counters
                if self.show_img:
                    cvzone.putTextRect(img_region, f'{"car:":<13}{len(self.carCount)}', (1020, 920), scale=2, thickness=1,
                                       offset=2, colorR=(0, 0, 0))
                    cvzone.putTextRect(img_region, f'{"motorbike:":<12}{len(self.motorbikeCount)}', (1020, 960), scale=2,
                                       thickness=1, offset=2,
                                       colorR=(0, 0, 0))
                    cvzone.putTextRect(img_region, f'{"truck:":<13}{len(self.truckCount)}', (1020, 1000), scale=2,
                                       thickness=1, offset=2, colorR=(0, 0, 0))
                    cvzone.putTextRect(img_region, f'{"bus:":<13}{len(self.busCount)}', (1020, 1040), scale=2, thickness=1,
                                       offset=2,
                                       colorR=(0, 0, 0))
                if self.verbose:
                    print(f'{"car:":<12}{len(self.carCount)}')
                    print(f'{"motorbike:":<12}{len(self.motorbikeCount)}')
                    print(f'{"truck:":<12}{len(self.truckCount)}')
                    print(f'{"bus:":<12}{len(self.busCount)}')

                if self.show_img:
                    # Define the scaling factor for the window
                    scaling_factor = 0.75  # You can adjust this value to your desired scale

                    # Calculate the scaled window size
                    scaled_width = int(img_region.shape[1] * scaling_factor)
                    scaled_height = int(img_region.shape[0] * scaling_factor)

                    # Create a named window with the scaled size
                    cv2.namedWindow("Scaled Window", cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Scaled Window", scaled_width, scaled_height)

                    cv2.imshow("Scaled Window", img_region)
                    # cv2.imshow("Vehicle counter", img_region)
                    cv2.waitKey(1)

                # Clearing the screen

                if not self.verbose:
                    print(f'\n{self.video_path}')
                    if (os.name == 'posix'):
                        os.system('clear')
                    else:
                        os.system('cls')

        cv2.destroyAllWindows()

        return len(self.carCount), len(self.motorbikeCount), len(self.busCount), len(self.truckCount)


if __name__ == "__main__":
    vehicle_counter = VehicleCounter()
    vehicle_counter.run()

