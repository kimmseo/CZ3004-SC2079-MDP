import time
import serial
from STM32 import STM32Server
from takepic import take_pic
import queue
import threading
from environment import Environment, Obstacle
import os
from com_path_mapping import map_commands_to_paths
from server_bt import BluetoothServer
from client_ir import ImageRecognitionClient

def ir_server(ir_queue, stm32_send_queue, ir_start_event, stm_start_event, shutdown_event):

    try:
        # Change to your laptop host ip when connected to RPI Wifi
        # use ipconfig to find your laptop host ip
        HOST = '192.168.19.21'
        PORT = 2030
        client = ImageRecognitionClient(HOST,PORT)  # Optionally pass host and port
        print("Connecting to Image Rec Server")
        client.connect()
        print("Connected...")

        SNAP_COUNT = 0

        while SNAP_COUNT < 4 and not shutdown_event.is_set():
            if not ir_queue.empty():
                ir_start_event.wait()
                ir_queue.get()

                SNAP_COUNT += 1
                print(f"SNAP COUNT {SNAP_COUNT}")

                file_path = take_pic()
                predict_id = client.send_file(file_path)
                stm32_send_queue.put(predict_id)
                stm_start_event.set()
                ir_start_event.clear()
    finally:
        print("Disconnecting from Image Rec Server")
        client.disconnect()


def STMSendServer(STM, stm32_recv_queue, stm_start_event, stm32_send_queue, stm_rcv_event, message_processed_event, shutdown_event):

    try:
        roundCount = 0
        reposition_command = ["FL090", "FW010", "FR090", "BW025", "FR090", "BW020"]

        while roundCount < 4 and not shutdown_event.is_set():
            roundCount += 1
            print("\nRound No. " + str(roundCount))

            if roundCount <= 1:
                command = "FW020"
                STM.send(command)
                stm32_recv_queue.put((command, ))
                stm_rcv_event.set()
                time.sleep(5.0)

            else:
                print("roundCount >= 1")
                index = 0
                for command in reposition_command:
                    print(f"reposition command: {command}")
                    time.sleep(1.0)
                    STM.send(command)
                    stm32_recv_queue.put((command, index))
                    stm_rcv_event.set()
                    if index < 5:
                        message_processed_event.wait()  # Wait for the message to be processed
                        message_processed_event.clear()  # Reset the event for the next iteration
                    index += 1

            while True:
                if not stm32_send_queue.empty():
                    stm_start_event.wait()
                    predict_id = stm32_send_queue.get()
                    int_predict_id = int(predict_id)

                    print(f"predict id result {predict_id}")
                    print(f"type(predict_id): {type(predict_id)}")
                    print(f"type(int_predict_id): {type(int_predict_id)}")

                    if int_predict_id != -1 and int_predict_id != 41:
                        print("id is valid")
                        shutdown_event.set()
                    break
                    stm_start_event.clear()
    finally:
        print("Disconnecting from STM")
        STM.disconnect()


def STMRcvServer(STM, stm32_recv_queue, ir_queue, ir_start_event, stm_rcv_event, message_processed_event, shutdown_event):
    while not shutdown_event.is_set():
        if not stm32_recv_queue.empty():
            stm_rcv_event.wait()
            command, *optional = stm32_recv_queue.get()
            received_msg = None
            start_time = time.time()
            timeout = 5
            while True:

                received_msg = STM.recv()
                if received_msg == "R":
                    print("received_msg is R")
                    time.sleep(1.0)
                    break
                elif (time.time()-start_time>timeout):
                    print("Timeout waiting for R receive message")
                    break
            if optional:
                print(f"optional[0] is {optional[0]}")

            if not optional or optional[0] >= 5:
                ir_queue.put("SNAP")
                ir_start_event.set()
            else:
                message_processed_event.set()  # Signal that the message has been processed

if __name__ == "__main__":
    # # Queues for communication between threads
    ir_queue = queue.Queue()
    stm32_send_queue = queue.Queue()
    stm32_recv_queue = queue.Queue()

    # At the beginning of your main section
    ir_start_event = threading.Event()
    stm_start_event = threading.Event()
    stm_rcv_event = threading.Event()
    message_processed_event = threading.Event()
    shutdown_event = threading.Event()

    #STM Server
    STM = STM32Server()
    STM.connect()

    # Creating threads for each task
    threads = [
        threading.Thread(target=ir_server, args=(ir_queue, stm32_send_queue, ir_start_event, stm_start_event, shutdown_event)),
        threading.Thread(target=STMSendServer, args=(STM, stm32_recv_queue, stm_start_event, stm32_send_queue, stm_rcv_event, message_processed_event, shutdown_event)),
        threading.Thread(target=STMRcvServer, args=(STM, stm32_recv_queue, ir_queue, ir_start_event, stm_rcv_event, message_processed_event, shutdown_event)),
    ]

    # Starting threads
    for thread in threads:
        thread.start()

    # Waiting for all threads to complete before exiting the main thread
    for thread in threads:
        thread.join()

    print("Task completed.")

