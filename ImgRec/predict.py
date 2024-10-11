import cv2
import os
import time
import importlib.util
import supervision as sv
from ultralytics import YOLO

config_dir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(config_dir, 'PC_CONFIG.py')
spec = importlib.util.spec_from_file_location("PC_CONFIG", config_path)
PC_CONFIG = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PC_CONFIG)

class Predictor:
    def __init__(self):
        # Load a pre-trained yolov8n model
        self.model = YOLO("../weights/best_FullDS150E.pt") # replace model here
    #     self.print_class_ids()  # Print class IDs upon initialization

    # def print_class_ids(self):
    #     # Print all class names and their corresponding IDs
    #     for id, name in enumerate(self.model.names):
    #         print(f"ID: {id}, Name: {name}")

    # def predict_id(self, image_file_path, task_type):
    #     # Load the image
    #     image = cv2.imread(image_file_path)

    #     # Run inference on the image
    #     results = self.model(image)

    #     # Print results
    #     print(results)
    #     # Show annotation
    #     self.show_annotation(image, results)

    #     # Extract class name
    #     class_name, largest_size, detection_id = None, -1, None
    #     for result in results:  # Assuming 'results' is a list
    #         print(f"task_type is {task_type}")

    #         if task_type == "TASK_2":
    #             for prediction in result.predictions:
    #                 print(prediction)
    #                 class_name = prediction.class_name
    #                 detection_id = prediction.detection_id
    #                 if class_name != "Bullseye":
    #                     break
    #         else:
    #             for prediction in result.predictions:
    #                 print(prediction)
    #                 if largest_size == -1 or max(prediction.width, prediction.height) > largest_size:
    #                     largest_size = max(prediction.width, prediction.height)
    #                     class_name = prediction.class_name
    #                     detection_id = prediction.detection_id

    #     if class_name:
    #         print("class_name = " + class_name)
    #     else:
    #         print("class_name = None")

    #     return class_name, results, detection_id

    def predict_id(self, image_file_path, task_type):
        # Load the image
        image = cv2.imread(image_file_path)
        # Validation for image existence
        if image is None:
            print(f"Error: Could not read image at {image_file_path}")
            return None, None, None

        # Check the image size and resize if necessary
        if image.shape[0] != 640 or image.shape[1] != 640:
            image = cv2.resize(image, (640, 640))  # Resize to 640x640

        # Run inference on the image
        results = self.model(image)  # Directly pass the image

        # Print results
        print(results)

        # Show annotation (using YOLOv8's plotting capabilities)
        # results[0].show()

        # Extract class name, largest size, and detection ID
        class_name, largest_size, detection_id = None, -1, 0
        boxes = results[0].boxes.xyxy  # Get bounding boxes (x1, y1, x2, y2)
        scores = results[0].boxes.conf  # Get confidence scores
        class_ids = results[0].boxes.cls  # Get class IDs

        for i in range(len(boxes)):
            print(f"task_type is {task_type}")

            if task_type == "TASK_2":
                if int(class_ids[i]) != 16:  # Replace with the ID for "Bulls Eye"
                    class_name = results[0].names[int(class_ids[i])]  # Get class name
                    detection_id = i
                    break
                else:
                    print("Bullseye detected")
                    class_name = "bullseye"
                    detection_id = i
            else:
                # Determine the largest bounding box
                box_width = boxes[i][2] - boxes[i][0]
                box_height = boxes[i][3] - boxes[i][1]
                size = max(box_width, box_height)
                detection_id = i

                if largest_size == -1 or size > largest_size:
                    largest_size = size
                    class_name = results[0].names[int(class_ids[i])]
                    detection_id = i

        if class_name:
            print("class_name = " + class_name)
            timestamp = int(time.time())
            # Save the annotated image
            try:
                results[detection_id].save(f'../data/image-rec/annotated_images/{class_name}_{timestamp}.jpg')
            except:
                print("error in saving photo!")
        else:
            print("class_name = None")

        return class_name, results, detection_id


    # def show_annotation(self, image, results):
    #     # Create supervision annotators
    #     bounding_box_annotator = sv.BoundingBoxAnnotator()
    #     label_annotator = sv.LabelAnnotator()

    #     # Process results from YOLOv8
    #     detections = []
    #     for result in results:
    #         for detection in result.boxes.data:  # Accessing YOLOv8's box data
    #             class_id = int(detection[5])  # Class ID
    #             x1, y1, x2, y2 = map(int, detection[:4])  # Bounding box coordinates
    #             score = float(detection[4])  # Confidence score

    #             # Add to detections
    #             detections.append({
    #                 "bbox": [x1, y1, x2, y2],
    #                 "confidence": score,
    #                 "class_id": class_id
    #             })

    #     # Convert detections to the expected format for supervision
    #     if detections:
    #         detections = sv.Detections(
    #             xyxy=[d["bbox"] for d in detections],
    #             confidence=[d["confidence"] for d in detections],
    #             class_id=[d["class_id"] for d in detections]
    #         )

    #         # Annotate the image with inference results
    #         annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    #         annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

    #         # Display the annotated image
    #         try:
    #             cv2.imshow("Annotated Image", annotated_image)
    #             cv2.waitKey(0)  # Wait indefinitely until a key is pressed
    #         except Exception as e:
    #             print(f"Error displaying image: {e}")
    #         finally:
    #             cv2.destroyAllWindows()  # Close all OpenCV windows
    #     else:
    #         print("No detections found.")


if __name__ == "__main__":
    # Example usage
    predictor = Predictor()
    # Specify the path to your image
    image_file_path = os.path.join(PC_CONFIG.FILE_DIRECTORY, "image-rec", "sample_images", "IMG_9325.jpg")
    # Predict and display the class name
    predictor.predict_id(image_file_path, "TASK_1")
