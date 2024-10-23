from threading import Lock
from picamera import PiCamera
from time import sleep
from datetime import datetime

# Create a global lock instance
camera_lock = Lock()

def take_pic():
    folder_path = "images/"
    now = datetime.now()
    image_name = now.strftime("image_%Y-%m-%d_%H-%M-%S.jpg")
    image_path = folder_path + image_name
    print(image_path)

    with camera_lock:
        # Use the camera as a context manager
        with PiCamera() as camera:
            camera.resolution = (640, 640)
            camera.rotation = 180
            sleep(0.1)  # Camera warm-up time
            camera.capture(image_path)
            print("Image captured and saved")

    return image_path

if __name__ == "__main__":
    take_pic()
