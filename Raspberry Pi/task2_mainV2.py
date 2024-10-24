import time
from multiprocessing import Process, Queue, Event, Value
import ctypes
from datetime import datetime
import json
from takepicV0 import take_pic

from server_bt import BluetoothServer
from http_client_ir import ImageRecognitionClient
from STM32 import STM32Server
from config import PC_CONFIG

DISCONNECT_MESSAGE = "!DISCONNECT"


def startBTServer(bt_queue, cmd_queue, ir_queue, stm32_send_queue, stm32_recv_queue,
                    cmd_start_event, ir_start_event, stm_start_event):
    print("Connecting to Android Bluetooth...")
    bt_server = BluetoothServer()
    receive_data = None

    try:
        while True:
            receive_data = bt_server.receive_data()
            if receive_data:  # Ensure receive_data_str is not None or empty
                print(f"Received data from Android: {receive_data}")

                try:
                    if receive_data == "START/PATH":
                        print(f"Processing START/PATH command: {receive_data}")
                        break 
                    else:
                        # Handle other data types or commands
                        print(f"Received other type of command: {receive_data}")
                        continue
                except:
                    continue
            else:
                print("No data received, or connection lost. Retrying...")

        cmd_queue.put_nowait(receive_data)

        while True:
            if not bt_queue.empty():
                msg = bt_queue.get()

                if msg == "FIN":
                    print(f"FIN msg: {msg}\n")
                    msg_to_android = f"FINISH/PATH"
                    print(f"sending {msg_to_android} to android")
                    bt_server.send_data(msg_to_android)
                    time.sleep(0.1)
                    break

        # delay the disconnection
        time.sleep(10)
        msg = "FIN"
        ir_queue.put(msg)
        stm32_send_queue.put(msg)

        cmd_start_event.set()
        ir_start_event.set()
        stm_start_event.set()
        stm32_recv_queue.put(msg)
        

    finally:
        print("Disconnecting from Android Bluetooth")
        bt_server.close_connection()


def cmdGeneratorTemp(bt_queue, cmd_queue, ir_queue, stm32_send_queue,
                        cmd_start_event, ir_start_event, stm_start_event):
    while True:
        # STAGE 1
        # Go forward using ultrasonic sensor towards obstacle 1 
        while True:
            if not cmd_queue.empty():
                msg = cmd_queue.get_nowait()
                command = "US040"
                stm32_send_queue.put(command)
                stm_start_event.set()
                break
        # Take pic and do image rec for obstacle 1
        cmd_start_event.wait()
        ir_queue.put("SNAP")
        ir_start_event.set()
        cmd_start_event.clear()
        # Check sign of first obstacle
        # Default go Left
        cmd_start_event.wait()
        direction = "L"
        predict_id = -1
        predict_id = cmd_queue.get()
        if predict_id == "38":
            direction = "R"
        if predict_id == "-1":
            print("Failed to identify left or right for Obstacle 1, going left by default.")    
        # Default left commands
        # commands = ["FL060", "FR060", "FW035", "FR060", "FL060", "US030"]
        commands = [ 'FL045','FW020','FR045','FW011','FR060','FL060','US125']
        if direction == "R":
            # commands = ["FR060", "FL060", "FW035", "FL060", "FR060","US030"]
            commands =   ['FR045','FW020','FL045','FW011','FL060','FR060','US125']
        # Send commands to STM to navigate pass obstacle 1
        cmd_start_event.set()
        for command in commands:
            cmd_start_event.wait()
            stm32_send_queue.put(command)
            stm_start_event.set()
            cmd_start_event.clear()
        
        # STAGE 2
        # Take image and do image rec for obstacle 2
        cmd_start_event.wait()
        ir_queue.put("SNAP")
        ir_start_event.set()
        cmd_start_event.clear()
        # Check sign of second obstacle
        # Default go Left
        cmd_start_event.wait()
        direction = "L"
        predict_id = -1
        predict_id = cmd_queue.get()
        print(f"Predicted ID from CMD queue: {predict_id}")
        print(f"Direction obtained: {direction}")
        if predict_id == "38":
            direction = "R"
        if predict_id == "-1":
            print("Failed to identify left or right for Obstacle 2, going left by default.")
        # command to navigate around obstacle 2
        # assuming:
            # turn to face side 
            # IR until edge of obstacle 2
            # turn corner to go to back of obstacle 2
            # IR until opposite edge of obstacle 2
            # turn corner to go back to front of obstacle 2 again 
        # Default left commands
        # commands = ["FL090", "FW015",                   
        #             "FR090", "FW003", "FR090",                 
        #             "FW070",                    
        #             "FR090", "FW003"] 
        commands = ['FL090','FW025',
                        'FR090','FW010','FR090','FW095','FR090',
                        'RT040','FW000','FR090','FW020','FL090','US015']
        if direction == "R":
            # commands = ["FR090", "FW015",                      
            #             "FL090", "FW003", "FL090",
            #             "FW070",                    
            #             "FL090","FW003"] 
             commands = ['FR090','FW018',
                         'FL090','FW010','FL090','FW090','FL090',
                        'RT040', 'FW000', 'FL090','FW020','FR090','US015']
        # Send commands to STM to navigate around obstacle 2 and # Go back to the carpark
        cmd_start_event.set()
        for command in commands:
            cmd_start_event.wait()
            stm32_send_queue.put(command)
            stm_start_event.set()
            cmd_start_event.clear()

        bt_queue.put("FIN")
        # wait for bt to send "FINISH/PATH" and set cmd_start_event
        cmd_start_event.wait()
        break


def startIRClient(ir_queue, cmd_start_event, ir_start_event):
    HOST = PC_CONFIG.HOST
    PORT = PC_CONFIG.IMAGE_REC_PORT
    client = ImageRecognitionClient(HOST,PORT)  # Optionally pass host and port
    print("Testing Connection to IR Server...")
    # Test - Check server status
    status_response = client.check_status()  # This method should make a GET request to the /status endpoint

    if status_response and status_response.get('status') == 'OK':
        print("[CONNECTED] to IR Server\n")
        while True:
            if not ir_queue.empty():
                ir_start_event.wait()
                msg = ir_queue.get()
                if msg == "FIN":
                    break

                file_path = take_pic()
                predict_id = None
                startTime = datetime.now()
                response = client.send_file(file_path, "C", "TASK_2")
                endTime = datetime.now()
                totalTime = (endTime - startTime).total_seconds()
                print(f"Time taken for Receiving Image = {totalTime} s")

                if response is not None:  # Check if response is not None
                    predict_id = response.get('predicted_id')
                # predict_id = 39
                if not predict_id:
                    print("predict id is None, changing to -1")
                    predict_id = "-1"
                
                cmd_queue.put(predict_id)
                cmd_start_event.set()
                ir_start_event.clear()
        client.display_stitched()
    else:
        print("Failed to connect to the IR server or IR server returned an unexpected status.")

def stmSendProcess(STM, stm32_send_queue, stm32_recv_queue, stm_start_event):
    while True:
        if not stm32_send_queue.empty():
            stm_start_event.wait()
            msg = stm32_send_queue.get()
            if msg == "FIN":
                break
            print(f"stm32 queue msg = {msg}")
            STM.send(msg)
            stm32_recv_queue.put(msg)
            stm_start_event.clear()
            time.sleep(0.1)


def stmRecvProcess(STM, stm32_recv_queue, cmd_start_event):
    while True:
        if not stm32_recv_queue.empty():
            msg = stm32_recv_queue.get(timeout=3)
            if msg == "FIN":
                break

            start_time = time.time()
            timeout = 3
            received_msg = None
            while(True):
                received_msg = STM.recv()
                # print(f"Received from stm: {received_msg}")
                if received_msg == "R":
                    print(f"Received R from stm: {received_msg}")
                    break
                elif (time.time()-start_time>timeout):
                    print("Timeout waiting for R receive message")
                    break
                else:
                    time.sleep(0.1)
    
            cmd_start_event.set()


if __name__ == "__main__":
    # Queues for communication between process
    bt_queue = Queue()
    cmd_queue = Queue()
    ir_queue = Queue()
    stm32_send_queue = Queue()
    stm32_recv_queue = Queue()
    

    # At the beginning of your main section
    cmd_start_event = Event()
    ir_start_event = Event()
    stm_start_event = Event() 

    
    # init STM32 Server
    print("Connecting to STM...")
    STM = STM32Server()
    STM.connect()

    # Creating process for each task
    processes = [
        Process(target=startBTServer, args=(bt_queue, cmd_queue, ir_queue, stm32_send_queue, stm32_recv_queue,
                                            cmd_start_event, ir_start_event, stm_start_event)),

        Process(target=cmdGeneratorTemp, args=(bt_queue, cmd_queue, ir_queue, stm32_send_queue,
                                                cmd_start_event, ir_start_event, stm_start_event)),

        Process(target=startIRClient, args=(ir_queue, 
                                            cmd_start_event, ir_start_event)),

        Process(target=stmSendProcess, args=(STM, stm32_send_queue, stm32_recv_queue,
                                              stm_start_event)),
                                              
        Process(target=stmRecvProcess, args=(STM, stm32_recv_queue,
                                               cmd_start_event)),
        
    ]

    # Starting process
    for process in processes:
        process.start()

    # Waiting for all process to complete before exiting the main process
    for process in processes:
        process.join()

    print("Disconnecting from STM")
    STM.disconnect()

    print("Task completed.")
