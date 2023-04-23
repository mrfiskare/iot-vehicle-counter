from ultralytics import YOLO
import cv2
import cvzone
import math

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

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    for r in results:

        # Drawing bounding boxes around objects with cvzone

        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            bbox = x1, y1, w, h
            cvzone.cornerRect(img, bbox)

            # Rounding confidence to 2 decimals

            conf = math.ceil(box.conf[0] * 100) / 100

            # Getting the class name, using the pre-defined list of coco-classes

            cls = int(box.cls[0])

            # Printing the confidence and class name to the terminal and bounding box

            print(f'class: {classNames[cls]} {conf}')
            cvzone.putTextRect(img, f'{classNames[cls]} {conf}',
                               (max(0, x1), max(30, y1)),
                               scale = 0.8, thickness = 1)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
