#import os
#import serial
#from environment import Environment, Obstacle
#from com_path_mapping import map_commands_to_paths
import time
import json
import queue
import threading
from STM32 import STM32Server
from takepic import take_pic
from bluetooth_module import BluetoothServer
from http_client_ir import ImageRecognitionClient
from PC_module import PCServer

def ir_server(ir_queue, bt_send_queue, ir_start_event, run_complete_event, shutdown_event, bt_send_event):

    try:
        
        HOST = '192.168.19.20'
        PORT = 4000
        client = ImageRecognitionClient(HOST,PORT)  # Optionally pass host and port
        print("Connecting to Image Rec Server")
        client.connect()
        print("Connected...")
        
        SNAP_COUNT = 0

        collected_data = {
            "predicted_id": []
        }

        while not shutdown_event.is_set():
            if not ir_queue.empty():
                ir_start_event.wait()
                ir_queue.get()

                SNAP_COUNT += 1
                print(f"SNAP COUNT {SNAP_COUNT}")

                print("Taking Pic")
                file_path = take_pic() # take pic using cam
                print("Getting Prediction from Image Recognition")
                prediction = client.send_file(file_path) # prediction from image_rec
                predicted_id = prediction.get('predicted_id')

                if predicted_id:
                    collected_data["predicted_id"].append(predicted_id)
                    print(f"Appended predicted_id: {predicted_id}")

                
                #stm32_send_queue.put(predict_id)
                #add something to implement the compiling of results

                #stm_start_event.set() # allows the next command to be sent
                ir_start_event.clear() # allows the ir to run again 

            if run_complete_event.is_set():
                bt_send_queue.put(collected_data) # put final results into queue for sending to android
                bt_send_event.set() # signal bt to send to android
    finally:
        print("Disconnecting from Image Rec Server")
        client.disconnect()


def STMSendServer(STM, stm_start_event, stm32_send_queue, stm_rcv_event, shutdown_event):

    try:

        #NO MORE ROUNDS

        #send all commands in one shot
        #receive all data in one shot (in diff server)

            # we issue a shutdown after stm sends us "done"
            # - this should happen after we get all our predictions

        #while not shutdown_event.is_set() and not pc_recv_queue.empty():

        while not shutdown_event.is_set():
            stm_start_event.wait()
            print("Sending Commands to STM")
            commands = stm32_send_queue.get()
            STM.send(commands) # send the algorithm commands to STM

            stm_rcv_event.set() # now we can get messages from STM

        #OPTIONAL, wait for ACK that all commands were received
            
    finally:
        print("Disconnecting STM")
        STM.disconnect()
    

def STMRcvServer(STM, stm32_recv_queue, ir_queue, ir_start_event, stm_rcv_event, shutdown_event, run_complete_event):
    while not shutdown_event.is_set():
        if not stm32_recv_queue.empty():
            stm_rcv_event.wait()
            #command, *optional = stm32_recv_queue.get() # we dont need the commands though
            #received_msg = None
            start_time = time.time()
            timeout = 5
            while True:
                
                print("Waiting for message from STM")
                received_msg = STM.recv() # message from STM to take pic or signal end of run
                print(f"Received Message: {received_msg}")

                if received_msg == "P":
                    print("Starting Photo Taking")
                    ir_queue.put("SNAP")
                    ir_start_event.set()
                    break

                elif received_msg == "D":
                    print("Robot has completed the Path")
                    stm_rcv_event.clear() # will stop waiting for messages
                    run_complete_event.set() # set this event to send results to bluetooth
                    break

                elif (time.time()-start_time>timeout):
                    print("Timeout waiting for R receive message")
                    break               


def BTSendServer(BT, shutdown_event, bt_send_event, bt_send_queue):
    try:
        while not shutdown_event.is_set():
            bt_send_event.wait() # wait until get signal to send | sent my stm send server
            print("Getting results")
            results = bt_send_queue.get()# the whole result will be in some queue 

            #Serialize JSON to string
            result_str = json.dumps(results)

            print("Sending results to Android")
            BT.android_send(result_str) # send to android the results of the run
            bt_send_event.clear() # stop expecting messages from android (might not be necessary)
            
            print("The run is over.")
            shutdown_event.set() # the run is over
    finally:
        print("Disconnecting Bluetooth")
        BT.bluetooth_disconnect()


def BTRcvServer(shutdown_event, BT, bt_recv_queue, pc_send_event):
    while not shutdown_event.is_set():
        print("Waiting to receive Layout from Android")
        layout = BT.android_receive()
        bt_recv_queue.put(layout) # put layout into
        pc_send_event.set() # start the event in PCRcvServer

    
def PCSendServer(PC, shutdown_event, pc_send_event, bt_recv_queue, pc_recv_event):
    try:
        while not shutdown_event.is_set():
            pc_send_event.wait()
            sending_layout = bt_recv_queue.get()
            print("Sending Layout to Algorithm")
            PC.PC_send(sending_layout)
            pc_recv_event.set()
    
    finally:
        print("Disconnecting PC")
        PC.PC_disconnect()


def PCRcvServer(shutdown_event, pc_recv_event, PC, stm32_send_queue, stm_start_event):
    while not shutdown_event.is_set():
        pc_recv_event.wait()
        print("Receiving Commands from Algorithm")
        commands = PC.PC_receive() # get the algorithm from Algo
        stm32_send_queue.put(commands) # put the commands inside of stm32 send queue
        
        stm_start_event.set() # start the sending of commands to STM


if __name__ == "__main__":
    # # Queues for communication between threads
    ir_queue = queue.Queue()

    stm32_send_queue = queue.Queue()
    stm32_recv_queue = queue.Queue()

    bt_send_queue = queue.Queue()
    bt_recv_queue = queue.Queue()

    pc_send_queue = queue.Queue()
    pc_recv_queue = queue.Queue()
        
    # At the beginning of your main section
    ir_start_event = threading.Event()

    stm_start_event = threading.Event()
    stm_rcv_event = threading.Event()

    bt_send_event = threading.Event()
    bt_rcv_event = threading.Event()

    pc_send_event = threading.Event()
    pc_recv_event = threading.Event()

    message_processed_event = threading.Event()
    shutdown_event = threading.Event()

    run_complete_event = threading.Event()

    #STM Server
    STM = STM32Server()
    STM.connect()

    #BT Server
    BT = BluetoothServer()
    BT.bluetooth_connect()

    #PC Server
    PC = PCServer()
    PC.PC_connect()

    # Creating threads for each task
    threads = [
        threading.Thread(target=ir_server, args=(ir_queue, stm32_send_queue, ir_start_event, stm_start_event, shutdown_event)),
        threading.Thread(target=STMSendServer, args=(STM, stm32_recv_queue, stm_start_event, stm32_send_queue, stm_rcv_event, message_processed_event, shutdown_event)),
        threading.Thread(target=STMRcvServer, args=(STM, stm32_recv_queue, ir_queue, ir_start_event, stm_rcv_event, message_processed_event, shutdown_event)),
        threading.Thread(target=BTSendServer, args=(BT, shutdown_event, bt_send_event, bt_send_queue)),
        threading.Thread(target=BTRcvServer, args=(shutdown_event, BT, bt_recv_queue, pc_send_event)),
        threading.Thread(target=PCSendServer, args=(PC, shutdown_event, pc_send_event, bt_recv_queue, pc_recv_event)),
        threading.Thread(target=PCRcvServer, args=(shutdown_event, pc_recv_event, PC, stm32_send_queue, stm_start_event)),
    ]

    # Starting threads
    for thread in threads:
        thread.start()

    # Waiting for all threads to complete before exiting the main thread
    for thread in threads:
        thread.join()

    print("Task completed.")

