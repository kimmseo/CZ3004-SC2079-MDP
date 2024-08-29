import os
import socket
import bluetooth
from time import sleep

RETRY_LIMIT = 10

class RPI_connection:
    """
    Hosted on Raspberry Pi as the server
    """

    def __init__(self):
        self.HOST = "192.168.22.22" #or whatever
        self.PORT = 5000
        
        self.android_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        #self.android_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bt_client_sock = ""
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pc_client_sock = ""
        
        self.msg_format: str = "utf-8"
        self.read_limit_bytes = 2048
        self.a_msg = ""
        self.pc_msg = ""
        
        
    def bluetooth_connect(self):
        print('Establishing connection with A7 Tablet')
        CHANNEL = 1        
        while True:
            try:
                # Close any existing socket before creating a new one
                self.android_socket.close()
                
                os.system("sudo hciconfig hci0 piscan")
                print("MDPGrp22 bluetooth is now discoverable")
                self.android_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.android_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.android_socket.bind(("", CHANNEL))
                self.android_socket.listen(1)

                self.bt_client_sock, address = self.android_socket.accept()
                print("Accepted connection from " + str(address))
                break
                
            except Exception as e:
                print("Connection with Android failed: " + str(e))
                # Close socket if it exists
                if self.bt_client_sock:
                    self.bt_client_sock.close()
                self.android_socket.close()
                CHANNEL+=1
                CHANNEL%=7
                print(f"Trying channel {CHANNEL}...")
                
                if CHANNEL == 1:
                    logger.error("Retried bluetooth connection 8 times, no success")
                    raise e
        
        
    def bluetooth_disconnect(self):
        print("Disconnecting bluetooth...")
        self.bt_client_sock.shutdown(socket.SHUT_RDWR)
        self.android_socket.shutdown(socket.SHUT_RDWR)
        self.bt_client_sock.close()
        self.android_socket.close()
        print("Disconnected Successfully")
        
    def PC_connect(self):    
        print(f'Establishing connection with PC, creating a server at {self.HOST}:{self.PORT}')
        TRIES = 0
        RETRY = True
        while RETRY and TRIES < RETRY_LIMIT:
            try:
                # Close any existing socket before creating a new one
                if self.pc_client_sock:
                    self.pc_client_sock.close()
                if self.socket:
                    self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.HOST, self.PORT))
                self.socket.listen()
                print("Listening for connection...")
                self.pc_client_sock, address = self.socket.accept()
                print(f"Connection from {address} established")
                RETRY = False
            except Exception as e:
                print("Connection with PC failed: " + str(e))
                # Close socket if it exists
                if self.pc_client_sock:
                    self.pc_client_sock.close()
                self.socket.close()
                TRIES += 1
                print(f"Retrying for the {TRIES} time...")
                sleep(1)
        
    def PC_disconnect(self):
        print("Closing socket...")
        self.pc_client_sock.shutdown(socket.SHUT_RDWR)
        self.pc_client_sock.close()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print("Socket closed")
        
    def android_send(self, message: str):
        self.bt_client_sock.send(message.encode(self.msg_format))
        
    def android_receive(self):
        self.a_msg = self.bt_client_sock.recv(self.read_limit_bytes).decode(self.msg_format)
        print(f"Received message from Android: {self.a_msg}")
        return self.a_msg
        
    def PC_send(self, message: str):
        self.pc_client_sock.send(message.encode(self.msg_format))
        
    def PC_receive(self):
        self.pc_msg = self.pc_client_sock.recv(self.read_limit_bytes).decode(self.msg_format)
        print(f"Received message from PC: {self.pc_msg}")
        return self.pc_msg
    
'''
Below is used to test the connections written in this .py file
Usage:
    1. Run 'python3 RPI_comms.py' in RPI terminal to run the connection test
    2. Connect RPI to android tablet via bluetooth (can use the S2 Terminal app)
    3. Run 'python3 PC_comms.py' in PC terminal 
    4. Connection all done. Begin testing now
'''
        
if __name__ == '__main__':
    
    rpi = RPI_connection()
    #from STM32PythonAbstractionAPI.robot_controller import RobotController
    #robot = RobotController('change_me_to_port', 115200)
    DIST = 10 # cm
    ANGLE = 90 # degrees

    rpi.bluetooth_connect()
    rpi.PC_connect()

    try:
        while True:
            print("-----------------------------------------------------------------------")
            print("You are currently in the connection test function. This function allows")
            print("you to test the connection between the RPI, STM, Android, or PC")
            print("-----------------------------------------------------------------------")
            print("Enter your choice of test:")
            print("1 -- Android to PC")
            print("2 -- PC to Android")
            print("3 -- Android to STM")
            print("4 -- PC to STM")
            choice = input()
            if choice == '1':
                print("Testing Android to PC communication. Type something on the tablet and the PC should show")
                rpi.PC_send("A-PC")
                while True:
                    message = rpi.android_receive()
                    print(f"Received {message}. Passing over to PC now")
                    rpi.PC_send(message)
                    if message == 'bye': 
                        message = ''
                        break
                
            elif choice == '2':
                print("Testing PC to Android communication. Type something on the PC and the tablet should show")
                rpi.PC_send("PC-A")
                while True:
                    message = rpi.PC_receive()
                    print(f"Received {message}. Passing over to android now")
                    rpi.android_send(message)
                    if message == 'bye': 
                        message = ''
                        break
                    
            # elif choice == '3':
            #     print("Testing Android to STM communication. Type W/A/S/D on the tablet and the robot should move")
            #     move = rpi.android_receive()
            #     if move == 'w' or move == 'W':
            #         robot.move_forward(DIST)
            #     elif move == 'a' or move == 'A':
            #         robot.turn_left(ANGLE, True)
            #     elif move == 's' or move == 'S':
            #         robot.move_backward(DIST)
            #     elif move == 'd' or move == 'D':
            #         robot.turn_left(DIST, True)
            #     else:
            #         break
                    
            # elif choice == '4':
            #     print("Testing PC to STM communication. Type W/A/S/D on the PC and the robot should move")
            #     move = rpi.PC_receive()
            #     if move == 'w' or move == 'W':
            #         robot.move_forward(DIST)
            #     elif move == 'a' or move == 'A':
            #         robot.turn_left(ANGLE, True)
            #     elif move == 's' or move == 'S':
            #         robot.move_backward(DIST)
            #     elif move == 'd' or move == 'D':
            #         robot.turn_left(DIST, True)
            #     else:
            #         break
                
            elif choice == 'q' or choice == 'quit' or choice == 'exit':
                rpi.PC_send("exit")
                break
            else:
                print("Invalid choice")
    except:    
        rpi.bluetooth_disconnect()
        rpi.PC_disconnect()
        
    finally:
        rpi.bluetooth_disconnect()
        rpi.PC_disconnect()