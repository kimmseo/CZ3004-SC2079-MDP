import sys
import time
from STM32 import STM32Server

def is_valid_command(command):
    """
    Check if each character of the command is either 'L' or 'R'.
    The command can be in lowercase or uppercase and must be exactly 2 characters long.
    """
    # Make the command uppercase to ensure case-insensitivity
    command = command.upper()
    # Check if the command length is exactly 2 and if each character is either 'L' or 'R'
    return len(command) == 2 and all(char in ['L', 'R', '0'] for char in command)

if __name__ == "__main__":
    if len(sys.argv) != 2 or not is_valid_command(sys.argv[1]):
        print("Invalid command format. The command must consist of two characters, each being either 'L' or 'R'.")
        sys.exit(1)

    STM = STM32Server()
    STM.connect()
    
    # Convert the first argument to uppercase to handle commands uniformly
    command = sys.argv[1].upper()
    first_direction = command[0]  # First character of the command
    second_direction = command[1]  # Second character of the command

    # Default left commands for first part
    first_part_commands = ['US040','US040',
                           'FL050','FW020','FR050','FW011',
                           'FR060','FL060','US125']
    
    # Right commands for first part
    if first_direction == "R":
        first_part_commands = ['US040','US040',
                               'FR050','FW020','FL050','FW010',
                               'FL060','FW011','FR060','US125']
        # first_part_commands = ['US040','US040',
        #                        'FR050','FW020','FL050','FW010',
        #                        'FL060','FR060','US125']
    elif first_direction == "0":
        first_part_commands = []


    # Default left commands for second part 
    # second_part_commands = ['FL090','IR030',
    #                         'FR090','FW010','FR090','IR130','FR090',
    #                         'RT040','FW000','FR090','RT000','FL090','US020']
    
    second_part_commands = ['FL090','IR130', 'FW007',
                            'FR090','FW010','FR090','IR030','FW003','FR090',
                            'RT040','FW000','FR090','RT100', "FL090", "US015", "US015"]

    # Right commands for second part
    if second_direction == "R":
        # second_part_commands = ['FR090','IR030',
        #                         'FL090','FW010','FL090','IR130','FL090',
        #                         'RT040', 'FW000', 'FL090','RT000','FR090','US020']
        
        second_part_commands = ['FR090','IR130', 'FW007',
                                'FL090','FW010','FL090','IR030','FW003','FL090',
                                'RT040', 'FW000', 'FL090','RT100', "FR090", "US015", "US015"]

    elif second_direction == "0":
        second_part_commands = []

    full_commands = first_part_commands + second_part_commands


    start_time = time.time()
    STM.send_command_list(full_commands)
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time Taken for commands: {time_taken} sec")

    STM.disconnect()