import time
import queue
import threading
import socket
import requests
import json
from environment import Environment, Obstacle
import os
from takepic import take_pic
from com_path_mapping import map_commands_to_paths

from server_bt import BluetoothServer
from STM32 import STM32Server

DISCONNECT_MESSAGE = "!DISCONNECT"

def startBTServer(stm32_queue, running_flag):
    print("Connecting to Android Bluetooth...")
    bt_server = BluetoothServer()
    receive_data = None

    while running_flag[0]:
        receive_data_str = bt_server.receive_data()
        print(f"\nReceived Message From Android: {receive_data_str}")
        print(f"Sending Message Back to Android: {receive_data_str}")
        bt_server.send_data(receive_data_str)
        
        if receive_data_str == "MOVE/F":
            print("Moving Forward)")
            stm32_queue.put("FW010")

        elif receive_data_str == "MOVE/B":
            print("Moving Backward")
            stm32_queue.put("BW010")
        time.sleep(0.2)


def startSTMServer(stm32_queue, running_flag):
    print("Connecting to STM...")
    STM = STM32Server()
    STM.connect()

    while running_flag[0]:
        if not stm32_queue.empty():
            msg = stm32_queue.get()

            print(f"Sending to STM: {msg}")
            STM.send(msg)
            received_msg = None
            while(True):
                received_msg = STM.recv()
                if received_msg:
                    break

if __name__ == "__main__":
    stm32_queue = queue.Queue()

    # Flag to control the execution of threads
    running_flag = [True]
    
   # Creating threads for each task
    threads = [
        threading.Thread(target=startBTServer, args=(stm32_queue, running_flag)),
        threading.Thread(target=startSTMServer, args=(stm32_queue, running_flag))
    ]

    # Starting threads
    for thread in threads:
        thread.start()

    # Waiting for all threads to complete before exiting the main thread
    for thread in threads:
        thread.join()

    print("Task completed.")

        

    




    