import os
import socket
import bluetooth
import sys
from time import sleep
import threading

RETRY_LIMIT = 10

class PCServer:
    def __init__(self):
        self.HOST = "192.168.19.1"
        self.PORT = 5000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pc_client_sock = None

        self.msg_format = "utf-8"
        self.read_limit_bytes = 2048
        self.a_msg = ""
        self.pc_msg = ""

    def PC_connect(self):
        print(f'Establishing connection with PC at {self.HOST}:{self.PORT}')
        TRIES = 0
        RETRY = True
        while RETRY and TRIES < RETRY_LIMIT:
            try:
                if self.pc_client_sock:
                    self.pc_client_sock.close()
                if self.socket:
                    self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((self.HOST, self.PORT))
                self.socket.listen()
                print("Listening for connection...")
                self.pc_client_sock, address = self.socket.accept()
                print(f"Connection from {address} established")
                RETRY = False
            except Exception as e:
                print("Connection with PC failed: " + str(e))
                if self.pc_client_sock:
                    self.pc_client_sock.close()
                self.socket.close()
                TRIES += 1
                sleep(1)

    def PC_disconnect(self):
        print("Closing PC socket...")
        if self.pc_client_sock:
            self.pc_client_sock.shutdown(socket.SHUT_RDWR)
            self.pc_client_sock.close()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print("PC socket closed")

    def PC_send(self, message: str):
        self.pc_client_sock.send(message.encode(self.msg_format))

    def PC_receive(self):
        self.pc_msg = self.pc_client_sock.recv(self.read_limit_bytes).decode(self.msg_format)
        print(f"Received message from PC: {self.pc_msg}")
        return self.pc_msg
    
if __name__ == '__main__':
    PC = PCServer()
    
    print("Connecting to PC")
    PC.PC_connect()
    print("PC has been connected")
    message = "PC has been connected"
    PC.PC_send(message)

    try :
        while True:
            print("Enter you choice")
            print("1 -- Enter a message to send to PC")
            print("2 -- Receive a message from PC")
            print("3 -- Exit")
            choice = input()

            if choice == '1':
                print("Enter your message")
                message = input()
                PC.PC_send(message)

            elif choice == '2':
                print("Enter your message on the PC")
                message = PC.PC_receive()
                print(f"Message Received : {message} ")

            elif choice == '3':
                print("Exiting connection")
                break
            else:
                print("Invalid Choice")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        PC.PC_disconnect()