import os
import socket
import bluetooth
from time import sleep
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BluetoothServer:
    def __init__(self):
        self.msg_format = "utf-8"
        self.read_limit_bytes = 2048
        self.server_socket = None
        self.client_socket = None
        self.initialize_bluetooth()

    def initialize_bluetooth(self):
        print('Establishing Bluetooth server on Raspberry Pi')
        CHANNEL = 1
        
        while True:
            try:
                # Close any existing socket before creating a new one
                if self.server_socket:
                    self.server_socket.close()
                
                os.system("sudo hciconfig hci0 piscan")
                print("Bluetooth is now discoverable")
                self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.server_socket.bind(("", CHANNEL))
                self.server_socket.listen(1)

                uuid = "00001101-0000-1000-8000-00805F9B34FC"
                bluetooth.advertise_service(self.server_socket, "RaspberryPiServer",
                                            service_id=uuid,
                                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

                print(f"Waiting for connection on RFCOMM channel {CHANNEL}")
                self.client_socket, client_info = self.server_socket.accept()
                print(f"Accepted connection from {client_info}")
                break
                
            except Exception as e:
                print(f"Bluetooth server setup failed: {e}")
                if self.server_socket:
                    self.server_socket.close()
                CHANNEL += 1
                CHANNEL %= 30  # Using a wider range of channels
                print(f"Trying channel {CHANNEL}...")
                
                if CHANNEL == 1:
                    logger.error("Retried bluetooth connection 30 times, no success")
                    raise e

    def receive_data(self):
        try:
            data = self.client_socket.recv(self.read_limit_bytes)
            return data.decode(self.msg_format)
        except IOError as e:
            print(f"Error receiving Bluetooth data: {e}")
            return None

    def send_data(self, data):
        try:
            self.client_socket.send(data.encode(self.msg_format))
        except Exception as e:
            print(f"Error sending Bluetooth data: {e}")

    def close_connection(self):
        print("Closing Bluetooth connection...")
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                print(f"Error closing client socket: {e}")
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                print(f"Error closing server socket: {e}")
        
        print("Bluetooth connection closed")

if __name__ == "__main__":
    server = BluetoothServer()
    try:
        while True:
            data = server.receive_data()
            if data:
                print(f"Received: {data}")
                # Process the data as needed
                response = f"Raspberry Pi received: {data}"
                server.send_data(response)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        server.close_connection()
