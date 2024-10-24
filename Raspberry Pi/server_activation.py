import subprocess
from config import PC_CONFIG


if __name__ == '__main__':
    
    subprocess.Popen(["python", PC_CONFIG.FILE_DIRECTORY + "image-rec\\http_server_ir.py"])
    # subprocess.Popen(["python", PC_CONFIG.FILE_DIRECTORY + "Algorithm\\Task 1\Algorithm\\Main_V2.py"])
    subprocess.Popen(["python", PC_CONFIG.FILE_DIRECTORY + "Algorithm\\Task 1\Algorithm\\Main.py"])

