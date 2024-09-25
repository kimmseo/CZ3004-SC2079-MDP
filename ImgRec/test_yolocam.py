import cv2
import numpy as np
from ultralytics import YOLO

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize YOLOv8 model
model = YOLO('/Users/xot/Documents/UniversityWork/Y4S1/MDP/ImgRecAaron/weights/newL_best.pt')  # Replace with the path to your model

# Set the input size
INPUT_SIZE = (640, 640)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame to 640x640
    resized_frame = cv2.resize(frame, INPUT_SIZE)

    # Run YOLOv8 inference on the resized frame
    results = model(resized_frame)

    # Visualize the results on the original frame
    annotated_frame = results[0].plot()

    # Resize the annotated frame back to the original size for display
    annotated_frame = cv2.resize(annotated_frame, (frame.shape[1], frame.shape[0]))

    # Display the annotated frame
    cv2.imshow("YOLOv8 Inference", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()