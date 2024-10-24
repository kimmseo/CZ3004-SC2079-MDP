import requests
from config import PC_CONFIG

class ImageRecognitionClient:
    def __init__(self, host, port):
        self.server_url = f"http://{host}:{port}"

    def check_status(self):
        """Check the status of the server."""
        response = requests.get(f"{self.server_url}/status")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error checking status: {response.status_code}")
            return None

    def send_file(self, file_path, direction, task_type):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'direction': direction, 'task_type': task_type}
            response = requests.post(f"{self.server_url}/upload", files=files, data=data)
            if response.status_code == 200:
                print("File sent to the server successfully.")
                print(response.json())
                return response.json()
            else:
                print("Failed to send file to the server.")
                print(response.text)
                return None   
        
    def display_stitched(self):
        response = requests.post(f"{self.server_url}/display_stitched")
        if response.status_code == 200:
            print("Stitched request sent to the server successfully.")
            print(response.json())
            return response.json()
        else:
            print("Failed to send stitched request to the server.")
            print(response.text)
            return None   

if __name__ == "__main__":
    host = PC_CONFIG.HOST
    port = PC_CONFIG.IMAGE_REC_PORT
    client = ImageRecognitionClient(host, port)
    client.send_file('/path/to/your/image.jpg', 'north')  # Adjust the file path and direction as needed
