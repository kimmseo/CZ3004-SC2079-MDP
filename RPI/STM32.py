import time
import serial
import re  # Import the regex module

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
            start_time = time.time()
            timeout = 3
            pattern = r"^(RT)\d{3}$"
            while True:
                received_msg = self.recv()
                if received_msg == "R":
                    print(f"Received 'R' from STM: {received_msg}")
                    break
                elif (time.time()-start_time>timeout):
                    print("Timeout waiting for R receive message")
                    break
            if re.match(pattern, command):
                time.sleep(0.1)


if __name__ == "__main__":
    STM = STM32Server()
    STM.connect()


    commands = [
            "FW090",
            "FW003",
            "BR090",
            "BW002",
            "BW020",
            "FW003",
            "BR090",
            "BW002",
            "BW040",
            "FW003",
            "BL090",
            "BW002",
            "FW050",
            "BW090",
            "FW003",
            "BL090",
            "BW002",
            "FW010",
            "BW020",
            "FW003",
            "BL090",
            "BW002",
            "BW070",
            "FW003",
            "BR090",
            "BW002",
            "BW040",
            "FW003",
            "BL090",
            "BW002",
            "FW090",
            "FW010",
            "FW003",
            "FL090",
            "FW090",
            "FW030",
            "FW003",
            "BR090",
            "BW002",
            "FW020"]
    
    start_time = time.time()
    STM.send_command_list(commands)
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time Taken for commands: {time_taken} sec")

    STM.disconnect()