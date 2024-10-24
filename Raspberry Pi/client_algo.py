import requests

class AlgorithmClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def check_status(self):
        """Check the status of the server."""
        response = requests.get(f"{self.base_url}/status")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error checking status: {response.status_code}")
            return None

    def navigate(self, navigation_data):
        """Send navigation data to the server and get the path and commands."""
        response = requests.post(f"{self.base_url}/navigate", json=navigation_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error sending navigation data: {response.status_code}")
            return None

if __name__ == "__main__":
    #base_url = 'http://192.168.16.11:2040'  # The base URL where your Flask app is running
    base_url = 'http://192.168.19.19:5000'  # The base URL where your Flask app is running
    client = AlgorithmClient(base_url)
    
    # Check server status
    status = client.check_status()
    if status:
        print("Algo Server Status:", status)

    # Send navigation data
    navigation_data = {
        "type": "START/EXPLORE",
        "size_x": 20,
        "size_y": 20,
        "robot_x": 1,
        "robot_y": 1,
        "robot_direction": 0,
        "obstacles": [
            {"x": 5, "y": 6, "id": 1, "d": 4},
            {"x": 8, "y": 1, "id": 2, "d": 0},
            {"x": 11, "y": 10, "id": 3, "d": 2}
        ]
    }
    
    navigation_response = client.navigate(navigation_data)
    if navigation_response:
        print("Navigation Response:", navigation_response)
