import sys
import time
import re  # Import the regex module

from STM32 import STM32Server

def is_valid_command(command):
    """
    Check if the command matches the required format.
    The format is one of FW, BW, FL, FR, BL, BR followed by three digits.
    """
    pattern = r"^(FW|BW|FL|FR|BL|BR|US)\d{3}$"
    return re.match(pattern, command) is not None

if __name__ == "__main__":
    if len(sys.argv) != 2 or not is_valid_command(sys.argv[1]):
        print("Invalid command format. The command must be FW, BW, FL, FR, BL, BR followed by three digits.")
        sys.exit(1)

    STM = STM32Server()
    STM.connect()
    
    command = sys.argv[1]

    STM.send(command)
    print(f"Sent to STM: {command}")
    while True:
        received_msg = STM.recv()
        if received_msg == "R":
            print(f"Received 'R' from STM: {received_msg}")
            time.sleep(0.5)
            break


    STM.disconnect()
