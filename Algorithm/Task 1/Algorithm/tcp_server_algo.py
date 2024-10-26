import socket
import json

# Constants
HEADER = 64
PORT = 2040

# Change to your laptop host ip when connected to RPI Wifi
# use ipconfig to find your laptop host ip
#HOST = '192.168.151.23' # NTUSECURE
HOST = '192.168.19.21'
#HOST = '192.168.19.19'
#HOST = '192.168.80.20'

ADDR = (HOST, PORT)
FORMAT = 'utf-8'

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def create_response():
    # Create and return the JSON response
    response = {
            #"commands": ["FW015", "FIN"],
            "commands": ["FW010", "FW005", "BR001", "FW020", "FW005", "BR001", "SNAP1_R", "BR001", "FR000", "BW001", "BR000", "SNAP2_C", "FIN"],
            #"commands": ["FW090", "FW050", "BR000", "FW020", "FW020", "BR000", "SNAP1_R", "BR010", "FR000", "BW010", "BR000", "SNAP2_C", "FIN"],
            "distance": 46.0,
            "path": [{"d": 0, "s": -1, "x": 1, "y": 1}, {"d": 2, "s": -1, "x": 5, "y": 3}, {"d": 2, "s": -1, "x": 6, "y": 9}]
    }
    return json.dumps(response)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.\n")
    try:
        # Wait for an initial message from the client (optional, depending on your protocol)
        msg_length = conn.recv(HEADER).decode(FORMAT).strip()
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f"[{addr}] Received: {msg} \n")

            # Prepare and send the main JSON response
            response = create_response()
            response_bytes = response.encode(FORMAT)  # Encode the JSON string to bytes
            response_header = f"{len(response_bytes):<{HEADER}}".encode(FORMAT)  # Prepare the header
            print(f"Sending Response: {response} \n")
            conn.send(response_header + response_bytes)  # Send the header followed by the response
    except ConnectionResetError:
        print(f"[CONNECTION LOST] {addr} connection lost.\n")
    except Exception as e:
        print(f"[ERROR] {addr} encountered an error: {e}\n")

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}\n")
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    print("[STARTING] server is starting...\n")
    start()
