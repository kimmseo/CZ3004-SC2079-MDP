import time
import serial

class STM32Server:
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=115200):
        self.baud_rate = baud_rate
        self.serial_port = serial_port
        self.stm = None

    def connect(self):
        while True:
            try:
                print(f"[STM] Establishing Connection with STM on Serial Port: {self.serial_port} Baud Rate: {self.baud_rate}")
                self.stm = serial.Serial(port=self.serial_port, baudrate=self.baud_rate, timeout=None)
                print(f"[STM] Established connection on Serial Port: {self.serial_port} Baud Rate: {self.baud_rate}")
                print(f"[CONNECTED] to STM.")
                break
            except serial.SerialException as e:
                print(f"[Error] Failed to establish STM Connection: {e}. Retrying...")
                time.sleep(1.0)

    def disconnect(self):
        if self.stm:
            try:
                self.stm.close()
                self.stm = None
                print("[DISCONNECTED] from STM.")
            except serial.SerialException as e:
                print(f"[Error] Failed to disconnect STM: {e}")

    def recv(self):
        try:
            if self.stm.inWaiting() > 0:
                raw_data = self.stm.read(1)  # Read one byte
                data = raw_data.decode().strip()
                return data
        except serial.SerialException as e:
            print(f"[Error] Failed to receive from STM: {e}. Retrying...")

    def send(self, message):
        try:
            print(f"[STM] Sending message to STM: {message}")
            self.stm.write(message.encode())
            self.stm.flush()
        except serial.SerialException as e:
            print(f"[Error] Failed to send to STM: {e}")

    def send_command_list(self, commands):
        for command in commands:
            self.send(command)
            print(f"Sent to STM: {command}")
            while True:
                received_msg = self.recv()
                if received_msg == "R":
                    print(f"Received 'R' from STM: {received_msg}")
                    time.sleep(0.001)
                    break


if __name__ == "__main__":
    STM = STM32Server()
    STM.connect()

    # commands = ["FW020", "FW010", "FW030", "BW010", "BW010", "BW010", "FW010", "FW010", "FW010"]
    # commands = ["FL090", "BW010"]
    # commands = ["FW020",
    #             "FL090", "FW010", "FR090", "BW025", "FR090", "BW020",
    #             "FL090", "FW010", "FR090", "BW025", "FR090", "BW020",
    #             "FL090", "FW010", "FR090", "BW025", "FR090", "BW020"]

    #  US060
    ## SNAP_1
    commands = ["US055"]
    STM.send_command_list(commands)
    print("SNAP1")

    direction = "L"

    # First Obstacle L
    if direction == "L":
	    #commands = ["FL090", "FR090", "FW030", "FR090", "FL090"]
        commands = ["FL060", "FR060", "FW035", "FR060", "FL060"]
    # First Obstacle R
    elif direction == "R":
        commands = ["FR060", "FL060", "FW030", "FL060", "FR060"]
    else:
        print("Image Rec for Image 1 Failed")

    STM.send_command_list(commands)

    #  US030
    ## SNAP_2
    commands = ["US030"]
    STM.send_command_list(commands)
    print("SNAP2")   


     # Second Obstacle L
     # Second Obstacle R
    STM.disconnect()
