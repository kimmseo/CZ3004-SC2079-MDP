import os
import socket
import bluetooth
import sys
from time import sleep
import threading


class BluetoothServer:
    def __init__(self):
        self.HOST = "192.168.19.1"
        self.PORT = 5000

        self.android_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.bt_client_sock = None

        self.msg_format = "utf-8"
        self.read_limit_bytes = 2048
        self.a_msg = ""
        self.pc_msg = ""

    def bluetooth_connect(self):
        print('Establishing connection with A7 Tablet')
        CHANNEL = 1
        MAX_CHANNELS = 30  # RFCOMM channels range from 1 to 30
        retries = 0
        while retries < MAX_CHANNELS:
            try:
                # Close any existing socket before creating a new one
                if self.android_socket:
                    self.android_socket.close()

                os.system("sudo hciconfig hci0 piscan")
                print("Bluetooth is now discoverable on channel", CHANNEL)
                self.android_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.android_socket.bind(("", CHANNEL))
                self.android_socket.listen(1)

                self.bt_client_sock, address = self.android_socket.accept()
                print("Accepted connection from " + str(address))
                break

            except Exception as e:
                print(f"Connection with Android failed on channel {CHANNEL}: " + str(e))
                if self.bt_client_sock:
                    self.bt_client_sock.close()
                self.android_socket.close()

                CHANNEL += 1
                retries += 1

                if retries >= MAX_CHANNELS:
                    print("Retried bluetooth connection on all channels, no success")
                    raise e

                # Wait a bit before retrying to avoid rapid retries
                time.sleep(1)

    def bluetooth_disconnect(self):
        print("Disconnecting bluetooth...")
        if self.bt_client_sock:
            self.bt_client_sock.shutdown(socket.SHUT_RDWR)
            self.bt_client_sock.close()
        self.android_socket.close()
        print("Disconnected Successfully")


    def android_send(self, message: str):
        try:
            self.bt_client_sock.send(message.encode(self.msg_format))
        except Exception as e:
            print(f"Error while sending data: {e}")

    def android_receive(self):
        self.a_msg = self.bt_client_sock.recv(self.read_limit_bytes).decode(self.msg_format)
        print(f"Received message from Android: {self.a_msg}")
        return self.a_msg
    

if __name__ == '__main__':
    BT = BluetoothServer()
    
    print("Connecting to Bluetooth")
    BT.bluetooth_connect()
    print("Bluetooth has been connected")
    message = "Bluetooth has been connected"
    BT.android_send(message)

    try :
        while True:
            print("Enter you choice")
            print("1 -- Enter a message to send to Android")
            print("2 -- Receive a message from android")
            print("3 -- Exit")
            choice = input()

            if choice == '1':
                print("Enter your message")
                message = input()
                BT.android_send(message)

            elif choice == '2':
                print("Enter your message on the android device")
                message = BT.android_receive()
                print(f"Message Received : {message} ")

            elif choice == '3':
                print("Exiting connection")
                break
            else:
                print("Invalid Choice")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        BT.bluetooth_disconnect()

