'''
Takes a photo and uploads to flask server for image recognition works
'''

import picamera
import asyncio
import aiohttp
import requests
from io import BytesIO
from settings import PC, FLASK_PORT
import time
import threading
from Connection.RPI_comms import RPI_connection
import json


def start_camera():
    camera = picamera.PiCamera()
    camera.resolution = (1980, 1980)
    camera.start_preview()
    time.sleep(2)
    return camera


def take_photo():
    print("snap! picture taken")
    with picamera.PiCamera() as camera:
        camera.resolution = (1980, 1980)
        image_stream = BytesIO()
        camera.capture(image_stream, format='jpeg')  # take photo and save as given name
        image_stream.seek(0)
        files = {'image': ('camera_photo.jpg', image_stream, 'image/jpeg'), 'task2': 0}
        response = requests.post(f'http://{PC}:{FLASK_PORT}/upload', files=files)
        if response.status_code == 200:
            mdp_id = response.text
            print(mdp_id)
            time.sleep(1)
            return mdp_id
        else:
            print("Server Down or Image Rec failed!")
            return None


def take_photo2(camera, rpi: RPI_connection = None, obj_index: int = -1):
    # print("snap! picture taken")
    image_stream = BytesIO()
    camera.capture(image_stream, format='jpeg')
    image_stream.seek(0)
    print("snap! took a photo")
    files = {'image': ('camera_photo.jpg', image_stream, 'image/jpeg'), 'obj_index': obj_index}
    response = requests.post(f'http://{PC}:{FLASK_PORT}/upload', files=files)
    if response.status_code == 200:
        mdp_id = response.text
        mdp_id = json.loads(mdp_id)
        print(mdp_id['message'])
        if rpi is not None:
            rpi.android_send(mdp_id)
        return mdp_id
    elif response.status_code == 202:
        print("Waiting for class detected")
        return None
    else:
        print("Server Down or Image Rec failed! Response status code:", response.status_code)
        return None

    return 1
    """    with picamera.PiCamera() as camera:
        camera.resolution = (1200, 1200)
        image_stream = BytesIO()
        time.sleep(2)
        camera.capture(image_stream, format='jpeg')  # take photo and save as given name
        image_stream.seek(0)
        print("picture taken")
        files = {'image': ('camera_photo.jpg', image_stream, 'image/jpeg')}
        #response = requests.post(f'http://{PC}:{FLASK_PORT}/upload', files=files)
        requests.post(f'http://192.168.22.42:8080/upload', files=files)
        camera.stop_preview()
        camera.close()
        return "thanks", 202
        #if response.status_code == 200:
        #    mdp_id = response.text
        #    print(mdp_id)
        #    return mdp_id
        #else:
        #    print("Server Down or Image Rec failed!")
        #    return None
    """
def reset_images():
    response = requests.post(f'http://{PC}:{FLASK_PORT}/reset_images')

    if response.status_code == 200:
        print(response.text)
        return
    else:
        print("Server Down or something failed!")
        return None

def combine_images():
    response = requests.post(f'http://{PC}:{FLASK_PORT}/combine_images')

    if response.status_code == 200:
        print(response.text)
        return
    else:
        print("Server Down or something failed!")
        return None


def fire_and_forget(camera, rpi: RPI_connection, obj_index: int = -1):
    threading.Thread(target=take_photo2, args=(camera, rpi, obj_index)).start()

def fire_and_destroy():
    threading.Thread(target=reset_images).start()

if __name__ == '__main__':
    cam = start_camera()
    n = 3
    print("taking pics now")
    for i in range(8):
        fire_and_forget(cam, None, i)
        time.sleep(n)

    time.sleep(1)
    combine_images()
