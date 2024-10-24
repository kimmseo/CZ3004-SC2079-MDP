import time
from multiprocessing import Process, Queue, Event
from datetime import datetime
import json

from takepicV0 import take_pic
from com_path_mappingV2 import map_commands_to_paths

from server_bt import BluetoothServer
from client_algo import AlgorithmClient
from http_client_ir import ImageRecognitionClient
from STM32 import STM32Server
from config import PC_CONFIG

DISCONNECT_MESSAGE = "!DISCONNECT"

def startBTServer(bt_queue, algo_queue, ir_queue, stm32_send_queue, stm32_recv_queue,
                  bt_start_event, algo_start_event, ir_start_event, stm_start_event):
    print("Connecting to Android Bluetooth...")
    bt_server = BluetoothServer()
    receive_data = None

    try:
        while True:
            receive_data_str = bt_server.receive_data()
            if receive_data_str:  # Ensure receive_data_str is not None or empty
                print(f"Received data from Android: {receive_data_str}")

                try:
                    # Attempt to deserialize the JSON string into a dictionary
                    receive_data = json.loads(receive_data_str)  # Deserialize the JSON string into a dictionary
                    data_type = receive_data.get('type', '')

                    if data_type == "START/EXPLORE":
                        print(f"Processing START/EXPLORE command: {receive_data}")
                        break 
                    else:
                        # Handle other data types or commands
                        print(f"Received other type of command: {receive_data}")
                        continue

                except json.JSONDecodeError:
                    continue
                    # print("Received data is not valid JSON. Retrying...")
                    # Handle the case where the data is not valid JSON, possibly retry or log
            else:
                print("No data received, or connection lost. Retrying...")

        algo_queue.put_nowait(receive_data)
        algo_start_event.set()

        while True:
            if not bt_queue.empty():
                # bt_start_event.wait()

                msg = bt_queue.get()
                command, *optional_parts = msg  # Correct way to unpack

                if command == "STM32":
                    print(f"STM32 msg: {msg}")
                    if optional_parts:
                        msg, associated_path = optional_parts
                        for path in associated_path:  # Assuming associated_path is the list of dictionaries
                            x = path["x"]
                            y = path["y"]
                            direction_map = {0: "N", 2: "E", 4: "S", 6: "W"}
                            d = direction_map[path["d"]]
                            print(f"STM32 optional parts: msg = {msg}, x = {x}, y = {y}, d = {d}")
                            print(f"sending status to android: STATUS/Moving")
                            bt_server.send_data("STATUS/Moving")
                            time.sleep(0.1)
                            
                            msg_to_android = f"ROBOT/{x}/{y}/{d}"
                            print(f"sending robot to android: {msg_to_android}")
                            bt_server.send_data(msg_to_android)
                            time.sleep(0.1)

                
                elif command == "IR_CAPTURING":
                    print(f"IR_CAPTURING msg")
                    print(f"sending status to android: STATUS/Capturing")
                    bt_server.send_data("STATUS/Capturing")
                    time.sleep(0.1)


                elif command == "IR_TARGET":
                    print(f"IR TARGET msg: {msg}")
                    if optional_parts:  # This checks if there are any optional parts
                        # optional_parts is a list, handle accordingly
                        number_part, predict_id, direction = optional_parts
                        print(f"IR optional parts: Number part = {number_part}, Predict ID = {predict_id}, Direction = {direction}")
                        
                        msg_to_android = f"TARGET/{number_part}/{predict_id}"
                        print(f"sending target to android: {msg_to_android}")
                        bt_server.send_data(msg_to_android)
                        time.sleep(0.1)


                elif command == "FIN":
                    print(f"FIN msg: {msg}\n")
                    msg_to_android = f"FINISH/EXPLORE"
                    print(f"sending {msg_to_android} to android")
                    bt_server.send_data(msg_to_android)
                    time.sleep(0.1)
                    break
                else:
                    # Handle other commands or continue loop
                    time.sleep(0.1)
                    continue
                # start algo event at the end
                # bt_start_event.clear()
                if command != "IR_CAPTURING" and command != "STM32":
                    algo_start_event.set()

        # wait for android to stop timer before gracefully closing other processes
        # delay the disconnection
        time.sleep(10)
        msg = "FIN"
        ir_queue.put((msg,))
        stm32_send_queue.put((msg,))

        algo_queue.put_nowait((msg,))
        ir_start_event.set()
        stm_start_event.set()
        stm32_recv_queue.put((msg,))
    finally:
        print("Disconnecting from Android Bluetooth")
        bt_server.close_connection()



def startAlgoClient(algo_queue, ir_queue,
                    algo_start_event, bt_start_event, ir_start_event, stm_start_event):

    HOST = PC_CONFIG.HOST
    PORT = PC_CONFIG.ALGO_PORT
    base_url = f"http://{HOST}:{PORT}"
    client = AlgorithmClient(base_url)

    print("Testing Connection to Algo Server...")
    # Test - Check server status
    status_response = client.check_status()  # This method should make a GET request to the /status endpoint

    if status_response and status_response.get('status') == 'OK':
        print("[CONNECTED] to Algo Server\n")
        # Test - assume that msg received from android and is put into queue
        # algo_queue.put(1)
        while True:
            if not algo_queue.empty():
                msg = algo_queue.get_nowait()
                
                if isinstance(msg, (tuple)) and msg[0] == "FIN":
                    break

                # Example navigation data to send
                # msg = {"type":"START\/EXPLORE","size_x":20,"size_y":20,"robot_x":1,"robot_y":1,"robot_direction":0,"obstacles":[{"x":5,"y":6,"id":1,"d":4},{"x":8,"y":1,"id":2,"d":0},{"x":11,"y":10,"id":3,"d":2}]}

                response_received = None
                try_count = 1

                while not response_received and try_count <= 3:
                    response_received = client.navigate(msg)  # Updated to use the navigate method
                    try_count += 1

                if response_received:
                    print("\nExtracting the data from response:")
                    # Extracting the needed parts from response_received
                    commands_data = response_received.get("data", {})
                    commands = commands_data.get("commands", [])

                    distance = commands_data.get("distance", None)
                    path = commands_data.get("path", [])
                    print("Commands:", commands)
                    print("Distance:", distance)
                    print("Path:", path)

                    command_path = map_commands_to_paths({"commands": commands, "path": path})

                    substring = "SNAP"
                    mov_tup = ("FW", "BW", "FL", "FR", "BL", "BR")

                    if commands:
                        for command, associated_path in command_path:
                                algo_start_event.wait()

                                print(f"\nCommand: {command}")

                                if command.startswith(substring):
                                    parts = command.split("_")
                                    if len(parts) == 2:
                                        snap_command, direction = parts
                                        number_part = snap_command[len(substring):]
                                        ir_queue.put((substring, number_part, direction))
                                        algo_start_event.clear()
                                        ir_start_event.set()

                                elif command.startswith(mov_tup):
                                    stm32_send_queue.put((command, associated_path))
                                    if associated_path:
                                        bt_queue.put(("STM32", command, associated_path))
                                    algo_start_event.clear()
                                    stm_start_event.set()

                                elif command == "FIN":
                                    bt_queue.put((command,))
                                    # bt_start_event.set()

    else:
        print("Failed to connect to the Algo server or Algo server returned an unexpected status.")


def startIRClient(ir_queue, bt_queue, ir_start_event, bt_start_event):
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

                if msg[0] == "FIN":
                    break

                (substring, number_part, direction) = msg
                print(f"substring is {substring}")
                print(f"Taking a photo for obstacle no {number_part}")
                print(f"Direction is {direction}")
                # file_path = camera.take_pic()
                bt_queue.put(("IR_CAPTURING",))
                file_path = take_pic()
                
                predict_id = None
                startTime = datetime.now()
                task_type = "TASK_1"
                response = client.send_file(file_path, direction, task_type)
                endTime = datetime.now()
                totalTime = (endTime - startTime).total_seconds()
                print(f"Time taken for Receiving Image = {totalTime} s")

                if response is not None:  # Check if response is not None
                    predict_id = response.get('predicted_id')
                if not predict_id:
                    print("predict id is None, changing to -1")
                    predict_id = "-1"
                    
                bt_queue.put(("IR_TARGET", number_part, predict_id, direction))
                ir_start_event.clear()
                # bt_start_event.set()
        #camera.close()
        client.display_stitched()
    else:
        print("Failed to connect to the IR server or IR server returned an unexpected status.")

def stmSendProcess(STM, stm32_send_queue, stm32_recv_queue, stm_start_event):

    while True:
        if not stm32_send_queue.empty():
            stm_start_event.wait()
            msg =  stm32_send_queue.get()

            if msg[0] == "FIN":
                break

            (command, associated_path) = msg
            print(f"stm32 queue msg = {command}")
            STM.send(command)
            stm32_recv_queue.put((command, associated_path))
            stm_start_event.clear()
            time.sleep(0.1)


def stmRecvProcess(STM, stm32_recv_queue, bt_queue, bt_start_event, algo_start_event):
    while True:
        if not stm32_recv_queue.empty():
            msg = stm32_recv_queue.get(timeout=3)

            if msg[0] == "FIN":
                break

            (command , associated_path) = msg
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
                    time.sleep(0.01)

            algo_start_event.set()



if __name__ == "__main__":
    # Queues for communication between processes
    bt_queue = Queue()
    algo_queue = Queue()
    ir_queue = Queue()
    stm32_send_queue = Queue()
    stm32_recv_queue = Queue()

    # At the beginning of your main section
    bt_start_event = Event() 
    algo_start_event = Event()  
    ir_start_event = Event() 
    stm_start_event = Event() 

    # init STM32 Server
    print("Connecting to STM...")
    STM = STM32Server()
    STM.connect()

    # Creating processes for each task
    processes = [
        Process(target=startBTServer, args=(bt_queue, algo_queue, ir_queue, stm32_send_queue, stm32_recv_queue,
                                             bt_start_event, algo_start_event, ir_start_event, stm_start_event)),

        Process(target=startAlgoClient, args=(algo_queue, ir_queue,
                                               algo_start_event, bt_start_event, ir_start_event, stm_start_event)),

        Process(target=startIRClient, args=(ir_queue, bt_queue,
                                             ir_start_event, bt_start_event)),

        Process(target=stmSendProcess, args=(STM, 
                                             stm32_send_queue, stm32_recv_queue, 
                                             stm_start_event)),

        Process(target=stmRecvProcess, args=(STM, 
                                             stm32_recv_queue, bt_queue, 
                                             bt_start_event, algo_start_event))
    ]

    # Starting processes
    for process in processes:
        process.start()

    # Waiting for all processes to complete before exiting the main thread
    for process in processes:
        process.join()

    print("Disconnecting from STM")
    STM.disconnect()

    print("Task completed.")
