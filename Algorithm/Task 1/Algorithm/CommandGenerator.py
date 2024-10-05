from Direction import Direction

class CommandGenerator:
    def generate(states, obstacles):
        """
        This function takes in a list of states and generates a list of commands for the robot to follow

        Inputs
        ------
        states: list of State objects
        obstacles: list of obstacles, each obstacle is a dictionary with keys "x", "y", "d", and "id"

        Returns
        -------
        commands: list of commands for the robot to follow
        """

        # Convert the list of obstacles into a dictionary with key as the obstacle id and value as the obstacle
        obstacles_dict = {ob['id']: ob for ob in obstacles}

        # Initialize commands list
        commands = []

        # Iterate through each state in the list of states
        for i in range(1, len(states)):
            steps = "000"

            # If previous state and current state are the same direction,
            if states[i].direction == states[i - 1].direction:
                # Forward - Must be (east facing AND x value increased) OR (north facing AND y value increased)
                if (states[i].x > states[i - 1].x and states[i].direction == Direction.EAST) or (states[i].y > states[i - 1].y and states[i].direction == Direction.NORTH):
                    commands.append("FW010")
                # Forward - Must be (west facing AND x value decreased) OR (south facing AND y value decreased)
                elif (states[i].x < states[i-1].x and states[i].direction == Direction.WEST) or (
                        states[i].y < states[i-1].y and states[i].direction == Direction.SOUTH):
                    commands.append("FW010")
                # Backward - All other cases where the previous and current state is the same direction
                else:
                    commands.append("BW010")

                # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
                if states[i].screenshot_id != -1:
                    # NORTH = 0
                    # EAST = 2
                    # SOUTH = 4
                    # WEST = 6

                    current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
                    current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

                    # Obstacle facing WEST, robot facing EAST
                    if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                        if current_ob_dict['y'] > current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_L")
                        elif current_ob_dict['y'] == current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_C")
                        elif current_ob_dict['y'] < current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_R")
                        else:
                            commands.append(f"SNAP{states[i].screenshot_id}")

                    # Obstacle facing EAST, robot facing WEST
                    elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                        if current_ob_dict['y'] > current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_R")
                        elif current_ob_dict['y'] == current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_C")
                        elif current_ob_dict['y'] < current_robot_position.y:
                            commands.append(f"SNAP{states[i].screenshot_id}_L")
                        else:
                            commands.append(f"SNAP{states[i].screenshot_id}")

                    # Obstacle facing NORTH, robot facing SOUTH
                    elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                        if current_ob_dict['x'] > current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_L")
                        elif current_ob_dict['x'] == current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_C")
                        elif current_ob_dict['x'] < current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_R")
                        else:
                            commands.append(f"SNAP{states[i].screenshot_id}")

                    # Obstacle facing SOUTH, robot facing NORTH
                    elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                        if current_ob_dict['x'] > current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_R")
                        elif current_ob_dict['x'] == current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_C")
                        elif current_ob_dict['x'] < current_robot_position.x:
                            commands.append(f"SNAP{states[i].screenshot_id}_L")
                        else:
                            commands.append(f"SNAP{states[i].screenshot_id}")
                continue

            # If previous state and current state are not the same direction, it means that there will be a turn command involved
            # Assume there are 4 turning command: FR, FL, BL, BR (the turn command will turn the robot 90 degrees)
            # FR000 | FR030: Forward Right;
            # FL000 | FL030: Forward Left;
            # BR000 | BR030: Backward Right;
            # BL000 | BL030: Backward Left;

            # Facing north previously
            if states[i - 1].direction == Direction.NORTH:
                # Facing east afterwards
                if states[i].direction == Direction.EAST:
                    # y value increased -> Forward Right
                    if states[i].y > states[i - 1].y:
                        commands.append("FR{}".format("090"))
                    # y value decreased -> Backward Left
                    else:
                        commands.append("BL{}".format("090"))

                # Facing west afterwards
                elif states[i].direction == Direction.WEST:
                    # y value increased -> Forward Left
                    if states[i].y > states[i - 1].y:
                        commands.append("FL{}".format("090"))

                    # y value decreased -> Backward Right
                    else:
                        commands.append("BR{}".format("090"))
                else:
                    raise Exception("Invalid turing direction")

            # Facing east previously
            elif states[i - 1].direction == Direction.EAST:
                # Facing north afterwards
                if states[i].direction == Direction.NORTH:
                    # y value increased -> Forward Left
                    if states[i].y > states[i - 1].y:
                        commands.append("FL{}".format(steps))
                    # y value decreased -> Backward Right
                    else:
                        commands.append("BR{}".format(steps))

                # Facing south afterwards
                elif states[i].direction == Direction.SOUTH:
                    # y value increased -> Backward Left
                    if states[i].y > states[i - 1].y:
                        commands.append("BL{}".format(steps))
                    # y value increased -> Forward Right
                    else:
                        commands.append("FR{}".format(steps))
                else:
                    raise Exception("Invalid turing direction")

            # Facing south previously
            elif states[i - 1].direction == Direction.SOUTH:
                # Facing east afterwards
                if states[i].direction == Direction.EAST:
                    if states[i].y > states[i - 1].y:
                        # y value increased -> Backward Right
                        commands.append("BR{}".format(steps))
                    else:
                        # y value decreased -> Forward Left
                        commands.append("FL{}".format(steps))

                # Facing west afterwards
                elif states[i].direction == Direction.WEST:
                    if states[i].y > states[i - 1].y:
                        # y value increased -> Backward Left
                        commands.append("BL{}".format(steps))
                    else:
                        # y value decreased -> Forward Right
                        commands.append("FR{}".format(steps))
                else:
                    raise Exception("Invalid turing direction")

            # Facing west previously
            elif states[i - 1].direction == Direction.WEST:
                # Facing north afterwards
                if states[i].direction == Direction.NORTH:
                    # y value increased -> Forward Right
                    if states[i].y > states[i - 1].y:
                        commands.append("FR{}".format(steps))
                    # y value decreased -> Backward Left
                    else:
                        commands.append("BL{}".format(steps))

                # Facing south afterwards
                elif states[i].direction == Direction.SOUTH:
                    # y value increased -> Backwards Right
                    if states[i].y > states[i - 1].y:
                        commands.append("BR{}".format(steps))
                    # y value decreased -> Forward Left
                    else:
                        commands.append("FL{}".format(steps))
                else:
                    raise Exception("Invalid turing direction")
            else:
                raise Exception("Invalid position")

            # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
            if states[i].screenshot_id != -1:
                # NORTH = 0
                # EAST = 2
                # SOUTH = 4
                # WEST = 6

                current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
                current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

                # Obstacle facing WEST, robot facing EAST
                if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

                # Obstacle facing EAST, robot facing WEST
                elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

                # Obstacle facing NORTH, robot facing SOUTH
                elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

                # Obstacle facing SOUTH, robot facing NORTH
                elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

        # Final command is the stop command (FIN)
        commands.append("FIN")

        # Compress commands if there are consecutive forward or backward commands
        compressed_commands = [commands[0]]

        for i in range(1, len(commands)):
            # If both commands are BW
            if commands[i].startswith("BW") and compressed_commands[-1].startswith("BW"):
                # Get the number of steps of previous command
                steps = int(compressed_commands[-1][2:])
                # If steps are not 90, add 10 to the steps
                # if steps != 90:
                #     compressed_commands[-1] = "BW{}".format(steps + 10)
                #     continue

                if steps != 90:
                    if (steps + 10) < 100:
                        compressed_commands[-1] = "BW0{}".format(steps + 10)
                    else:
                        compressed_commands[-1] = "BW{}".format(steps + 10)
                    continue

            # If both commands are FW
            elif commands[i].startswith("FW") and compressed_commands[-1].startswith("FW"):
                # Get the number of steps of previous command
                steps = int(compressed_commands[-1][2:])
                # If steps are not 90, add 10 to the steps

                if steps != 90:
                    if (steps + 10) < 100:
                        compressed_commands[-1] = "FW0{}".format(steps + 10)
                    else:
                        compressed_commands[-1] = "FW{}".format(steps + 10)
                    continue

            # Otherwise, just add as usual
            compressed_commands.append(commands[i])

        return compressed_commands
