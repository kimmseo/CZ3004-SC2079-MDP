'''
This will be run on the RPI. Will be used to receive obstacle ID when available 
'''

from flask import Flask, request
from Connection.RPI_comms import RPI_connection
from settings import RPI_FLASK_PORT

class RPIFlaskServer:
    def __init__(self, rpi: RPI_connection = None):
        print("Starting RPI Flask Server...")
        self.app = Flask(__name__)
        self.host = '0.0.0.0'
        self.port = RPI_FLASK_PORT
        self.debug = False
        self.rpi = rpi

        @self.app.route('/class_detected', methods=['POST'])
        def print_message():
            message = request.data.decode('utf-8')
            self.handle_message(message)
            return 'thanks', 200

    def handle_message(self, message):
        message = message.strip('(').strip(')')
        obj_id, obj_index = message.split(',')
        obst_update = f"TARGET,{obj_index},{obj_id}"
        if self.rpi is not None:
            self.rpi.android_send(obst_update) if self.rpi is not None else print("Simulated send:", obst_update)

    def run_server(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)
        
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        

if __name__ == '__main__':
    server = RPIFlaskServer()
    server.run_server()

