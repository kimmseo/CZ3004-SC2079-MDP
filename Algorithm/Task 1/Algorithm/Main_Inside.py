import time
import math
from CommandGenerator import CommandGenerator
from Navigator_Inside import Navigator
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import importlib.util

app = Flask(__name__)
CORS(app)

# This is a health checkpoint
# Checks that Algorithm server is properly connected to RPi
@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "OK"})


@app.route("/navigate", methods=["POST"])
def path_finding():

    # Filter out content json file based on the format
    contentReceived = request.json
    try:
        content = contentReceived['value']
    except:
        content = contentReceived

    # For debugging - check that content is correct (content = obstacles)
    print(content)

    # size_x, size_y : Robot size
    size_x, size_y = 20, 20
    # robot_x, robot_y : Robot starting position
    # robot_direction : Robot's facing direction at the start
    robot_x, robot_y = 1, 1
    robot_direction = 0

    obstacles = content["obstacles"]
    for obs in obstacles:
        #print('Obs:', obs)
        if obs['x']==19:
            #print("Changing x to 18")
            obs['x']=18
        if obs['y']==18:
            #print("Changing y to 18")
            obs['y']=18
        if obs['x']==0:
            #print("Changing x to 1")
            obs['x']=1
        if obs['y']==0:
            #print("Changing y to 1")
            obs['y']=1
    print("Printing obs: ", obstacles)

    # Initialise Navigator object
    navigator = Navigator(size_x, size_y, robot_x, robot_y, robot_direction)

    # Add obstacle to Navigator
    for obstacle in obstacles:
        navigator.add_obstacle(
            obstacle["x"], obstacle["y"], obstacle["d"], obstacle["id"]
        )

    start = time.time()
    # Get shortest path
    optimal_path, distance = navigator.get_optimal_order_dp()
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")

    # Based on the shortest path, generate commands for the robot
    commands = CommandGenerator.generate(optimal_path, obstacles)

    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0

    # Debugging
    print("Commands Length: {}".format(len(commands)))

    transformed_commands = []

    for command in commands:
        print(command)
        if (
            command.startswith("SNAP")
            or command.startswith("FIN")
            or command[-1] != "0"
        ):
            continue
        elif (
            command.startswith("FW")
            or command.startswith("FS")
            or command.startswith("BW")
            or command.startswith("BS")
        ):
            i += int(command[2:]) // 10
        else:
            i += 1
        print("Current i: {}".format(i))
        direction_commands = {"FL": 2, "FR": 3, "BL": 3, "BR": 3}
        num_dicts_to_add = direction_commands.get(command[:2], 1)
        for _ in range(num_dicts_to_add):
            path_results.append(optimal_path[i].get_dict())

    # Adding additional commands for turning
    # Adjust/Remove needed for fine tuning
    # Inside Lab environment
    for command in commands:
        # Adjust turning angle (overshoot/undershoot)
        if command.startswith("FL"):
            transformed_commands.append("BW009")
            transformed_commands.append("FL087")
            transformed_commands.append("BW007")
        elif command.startswith("FR"):
            transformed_commands.append("BW005")
            transformed_commands.append("FR086")
            transformed_commands.append("BW007")
        elif command.startswith("BL"):
            transformed_commands.append("BW005")
            transformed_commands.append("BL085")
            #transformed_commands.append("BW002")
        elif command.startswith("BR"):
            transformed_commands.append("BW005")
            transformed_commands.append("BR088")
            #transformed_commands.append("BW002")
        # Fine tune FW and BW distance to match actual distance travelled by robot
        elif command.startswith("FW") or command.startswith("BW"): #or command.startswith("BW"):
            #print(command)
            transformed_distance = command[3:6]
            # Adjust ratio for FW and BW commands differently
            if command.startswith("FW"):
                transformed_distance = str(int(math.ceil(float(transformed_distance)*1.065)))
            elif command.startswith("BW"):
                transformed_distance = str(int(math.ceil(float(transformed_distance)*1.008)))
            else:
                continue
            if len(transformed_distance) == 1:
                command_to_append = command[:2] + "00" + transformed_distance
            else:
                command_to_append = command[:2] + "0" + transformed_distance
            if int(transformed_distance) >= 100:
                if int(transformed_distance) < 180:
                    diff = str(int(command_to_append[3:6]) - 90)
                    if len(diff) == 1:
                        diffCommand = command[:2] + "00" + diff
                    else:
                        diffCommand = command[:2] + "0" + diff
                    transformed_commands.append(command_to_append[:2] + "090")
                    transformed_commands.append(diffCommand)
                elif int(transformed_distance) > 180:
                    diff = str(int(command_to_append[3:6]) - 180)
                    if len(diff) == 1:
                        diffCommand = command[:2] + "00" + diff
                    else:
                        diffCommand = command[:2] + "0" + diff
                    transformed_commands.append(command_to_append[:2] + "090")
                    transformed_commands.append(command_to_append[:2] + "090")
                    transformed_commands.append(diffCommand)
                else:
                    transformed_commands.append(command_to_append[:2] + "090")
                    transformed_commands.append(command_to_append[:2] + "090")
            else:
                transformed_commands.append(command_to_append)

        else:  # For SNAP and FIN
            transformed_commands.append(command)
    # Debugging
    print(transformed_commands)
    return jsonify(
        {
            "data": {
                "distance": distance,
                "path": path_results,
                "commands": transformed_commands,
            },
            "error": None,
        }
    )

# Algorithm server runs on Port 8000
if __name__ == "__main__":

    try:
        # Construct the path to PC_CONFIG.py and import module
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'rpi', 'config'))
        config_path = os.path.join(config_dir, 'PC_CONFIG.py')
        spec = importlib.util.spec_from_file_location("PC_CONFIG", config_path)
        PC_CONFIG = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(PC_CONFIG)

        app.run(host=PC_CONFIG.HOST, port=PC_CONFIG.ALGO_PORT, debug=True)
    except:
        print('Unable to Connect to PC_CONFIG Host and Port. Switching to 0.0.0.0:8000.')
        app.run(host='0.0.0.0', port=8000, debug=True)
