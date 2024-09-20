import cv2
import os
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
        self.model = YOLO("/Users/xot/Documents/UniversityWork/Y4S1/MDP/SC2079-Multidisciplinary-Project-main/ImageRecognition/interface server/yolov10/models/128epoch.pt") # replace model here

    def predict_id(self, image_file_path, task_type):
        # Load the image
        image = cv2.imread(image_file_path)

        # Run inference on the image
        results = self.model.infer(image)

        # Print results
        print(results)
        # Show annotation
        self.show_annotation(image, results)

        # Extract class name
        class_name, largest_size, detection_id = None, -1, None
        for result in results:  # Assuming 'results' is a list
            print(f"task_type is {task_type}")
            
            if task_type == "TASK_2":
                for prediction in result.predictions:
                    print(prediction)                    
                    class_name = prediction.class_name
                    detection_id = prediction.detection_id
                    if class_name != "Bulls Eye":
                        break
            else:
                for prediction in result.predictions:
                    print(prediction)
                    if largest_size == -1 or max(prediction.width, prediction.height) > largest_size:
                        largest_size = max(prediction.width, prediction.height)
                        class_name = prediction.class_name
                        detection_id = prediction.detection_id

        if class_name:
            print("class_name = " + class_name)
        else:
            print("class_name = None")

        return class_name, results, detection_id

    def show_annotation(self, image, results):
        # Load the results into the supervision Detections API
        detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

        # Create supervision annotators
        bounding_box_annotator = sv.BoundingBoxAnnotator()
        label_annotator = sv.LabelAnnotator()
        
        # Annotate the image with inference results
        annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
        annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)
        
        # Display the annotated image
        cv2.imshow("Annotated Image", annotated_image)
        cv2.waitKey(3000)  # Display the image for 3 seconds
        cv2.destroyAllWindows()  # Close all OpenCV windows

if __name__ == "__main__":
    # Example usage
    predictor = Predictor()
    # Specify the path to your image
    image_file_path = os.path.join(PC_CONFIG.FILE_DIRECTORY, "image-rec", "sample_images", "IMG_9332.jpg")
    # Predict and display the class name
    predictor.predict_id(image_file_path, "TASK_1")
