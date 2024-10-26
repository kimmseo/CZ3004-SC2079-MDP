import cv2
import numpy as np
from ultralytics import YOLO

def get_camera_index():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

# Get available cameras
camera_indexes = get_camera_index()
print(f"Available cameras: {camera_indexes}")

# Try to use the last available camera (which is often an external or Continuity Camera)
camera_index = camera_indexes[-1] if camera_indexes else 0

# Initialize the webcam
cap = cv2.VideoCapture(camera_index)

# Initialize YOLOv8 model
model = YOLO('../weights/best_task2.pt')

# Set the input size
INPUT_SIZE = (720, 720)

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
