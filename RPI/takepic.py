from threading import Lock
from picamera import PiCamera
from time import sleep
from datetime import datetime

class CameraManager:
    def __init__(self):
        self.camera_lock = Lock()
        self.camera = PiCamera()
        self.camera.resolution = (640, 640)
        self.initialized = False

    def warm_up(self):
        with self.camera_lock:
            #self.camera.close()
            if not self.initialized:
                # Sleep to allow the camera's sensor to warm up
                sleep(2)  # Adjust time as needed
                self.initialized = True

    def take_pic(self):
        with self.camera_lock:
            if not self.initialized:
                self.warm_up()  # Warm up the camera if not already done
            
            now = datetime.now()
            folder_path = "images/"
            image_name = now.strftime("image_%Y-%m-%d_%H-%M-%S.jpg")
            image_path = folder_path + image_name

            self.camera.capture(image_path)
            print(f"Image captured and saved at {image_path}")

            #self.camera.close()

            return image_path

    def close(self):
        with self.camera_lock:
            self.camera.close()
            sleep(2.0)

if __name__ == "__main__":
    # Usage
    camera_manager = CameraManager()
    # Warm up the camera right after initialization if you expect to take a picture soon
    camera_manager.warm_up()
    # Take a picture
    image_path = camera_manager.take_pic()
    # When done with the camera, close it
    camera_manager.close()
