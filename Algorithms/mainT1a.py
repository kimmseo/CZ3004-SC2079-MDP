import asyncio
import math
from typing import List, Any
import photographer
from Connection.RPI_comms import RPI_connection
from RPI_flask import RPIFlaskServer
from multiprocessing import Process
from algo.algo import MazeSolver
from consts import Direction
from helper import command_generator
from stm32_api.dispatcher import BlockingDispatcher, _IO_Attr_Type
from stm32_api.robot_controller import RobotController
import time
from movement_update import MovementUpdate

# import pdb; pdb.set_trace()
CONST_ROBOT_START_X = 1
CONST_ROBOT_START_Y = 1
CONST_ROBOT_START_DIR = Direction.NORTH

robot = RobotController("/dev/ttyUSB0", 115200)
dispatcher = BlockingDispatcher(robot, 5, 2, u_if=_IO_Attr_Type.SIMULATED)
camera = None


async def turn_error_minimization(phi: float, offset_known: bool, phi_cur: float, sgn_offset: float = 0):
    if offset_known:

        if (phi + sgn_offset) >= 180:
            phi_opt = -180 + ((phi + sgn_offset) % 180)
        elif (phi + sgn_offset) < -180:
            phi_opt = ((phi + sgn_offset)) % 180
        else:
            phi_opt = (phi + sgn_offset)

        epsl = phi_opt - phi_cur
        if abs(epsl) <= 180:
            return abs(epsl), 1 if epsl > 0 else 0
        else:
            return 360 - epsl, 1 if epsl <= 0 else 0

    else:
        epsl_vars = []
        # basically repeat the above for all k in -2..2
        _CONST_ROT_MAG = 90
        for k in (-2, 3):
            if (phi + _CONST_ROT_MAG * k) >= 180:
                phi_opt = -180 + ((phi + _CONST_ROT_MAG * k) % 180)
            elif (phi + _CONST_ROT_MAG * k) < -180:
                phi_opt = (phi + _CONST_ROT_MAG * k) % 180
            else:
                phi_opt = (phi + _CONST_ROT_MAG * k)

            epsl = phi_opt - phi_cur
            if abs(epsl) <= 180:
                epsl_vars.append([abs(epsl), 1 if epsl > 0 else 0])
            else:
                epsl_vars.append([360 - epsl, 1 if epsl <= 0 else 0])
        n = 0
        for k, _ in enumerate(epsl_vars):
            if epsl_vars[k][0] < epsl_vars[n][0]:
                n = k
        return epsl_vars[n]


async def algo_process(obstacles: List[dict]) -> List[Any]:
    maze_solver = MazeSolver(20, 20, CONST_ROBOT_START_X, CONST_ROBOT_START_Y, Direction.NORTH, big_turn=None)

    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    for ob in obstacles:
        maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])
    print(obstacles)
    start = time.time()
    # Get shortest path
    optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=False)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")

    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)

    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]

    i = 0
    for command in commands:
        if command.startswith("SNAP"):
            continue
        if command.startswith("FIN"):
            continue
        elif command.startswith("FW") or command.startswith("FS"):
            i += int(command[2:]) // 10
        elif command.startswith("BW") or command.startswith("BS"):
            i += int(command[2:]) // 10
        else:
            i += 1
        path_results.append(optimal_path[i].get_dict())

    print(commands)
    return commands


def obst_cb(*args):
    print("Obstacle detected!")


async def translate_and_dispatch(cmds: List[str], rpi: RPI_connection = None):
    phi = await dispatcher.dispatchB(RobotController.get_yaw, [], obst_cb)
    di = []
    cur_offset = 0
    ctr = 0
    move = MovementUpdate(rpi)
    for cmd in cmds:
        if cmd.startswith("SNAP"):

            print("took picture")
            obj_index = int(cmd[4])
            print(obj_index)
            global camera
            if camera is None:
                camera = photographer.start_camera()
            photographer.fire_and_forget(camera, rpi, obj_index)
        else:
            fn_ptr = None
            args = []
            if cmd.startswith("FIN"):
                time.sleep(2)
                photographer.combine_images()
                return
            elif cmd.startswith("FW") or cmd.startswith("FS"): # forward
                fn_ptr = RobotController.move_forward
                args = [int(cmd[2:])]
                move.F(int(cmd[2:]))
            elif cmd.startswith("BW") or cmd.startswith("BS"): # backward
                fn_ptr = RobotController.move_backward
                args = [int(cmd[2:])]
                move.B(int(cmd[2:]))
            elif cmd.startswith("FL"): # forward left
                fn_ptr = RobotController.turn_left
                args = [90, 1]
                move.L(True)
            elif cmd.startswith("FR"): # forward right
                fn_ptr = RobotController.turn_right
                args = [90, 1]
                move.R(True)
            elif cmd.startswith("BL"): # backward left
                fn_ptr = RobotController.turn_left
                args = [90, 0]
                move.L(False)
            elif cmd.startswith("BR"): # backward right
                fn_ptr = RobotController.turn_right
                args = [90, 0]
                move.R(False)
            else:
                print("Invalid command")

            await dispatcher.dispatchB(fn_ptr, args, obst_cb)
            await asyncio.sleep(0.45)

            while robot.poll_is_moving():
                await asyncio.sleep(0.01)

            ctr += 1
            if id(fn_ptr) == id(RobotController.turn_left):
                cur_offset += 90
                if cur_offset > 180:
                    cur_offset = -180 + (cur_offset % 180)
            elif id(fn_ptr) == id(RobotController.turn_right):
                cur_offset -= 90
                if cur_offset < -180:
                    cur_offset %= 180

            if 1:
                phi_cur = await dispatcher.dispatchB(RobotController.get_yaw, [], obst_cb)
                e, sgn = await turn_error_minimization(phi, True, phi_cur, cur_offset)

                print([phi_cur, e, sgn])
                if e < 25:
                    await dispatcher.dispatchB(RobotController.turn_left if sgn else RobotController.turn_right,
                                               [math.floor(e), 1], obst_cb)
                if e > 165 and e < 180:
                    await dispatcher.dispatchB(RobotController.turn_right if sgn else RobotController.turn_left,
                                               [math.floor(180-e), 1], obst_cb)

                    while robot.poll_is_moving():  # If robot not moving
                        await asyncio.sleep(0.01)

    photographer.combine_images()
    
    return None


async def main():
    rpi = RPI_connection()

    print("Select choice of execution:")
    print("1. send map via android")
    print("2. send map via hardcoded map")
    choice = input()
    try:
        choice = int(choice)
    except:
        rpi.bluetooth_disconnect()
        return

    if choice == 1:
        rpi.bluetooth_connect()
        
        print("===========================Receive Obstacles Data===========================")
        print("Waiting to receive obstacle data from ANDROID...")
        obst_message = rpi.android_receive()
        rpi_flask = RPIFlaskServer(rpi)
        rpi_flask_process = Process(target=rpi_flask.run_server)
        rpi_flask_process.start()
        try:
            obstacles = parse_android_message(obst_message)
            cmd = await algo_process(obstacles)
            photographer.fire_and_destroy()
            print("\n\nAlg path computed. Press start and all the best!")
            while True:
                if ("start" == rpi.android_receive()):
                    break 
                
            await translate_and_dispatch(cmd, rpi)

            # algo here
            # asyncio.run(app.execute())
            print("finished Task 1")
        except Exception as e:
            print(e)

    elif choice == 2:
        #obst_message = 'OBS|15,14,N,1|16,6,W,2|8,10,S,3|3,18,S,4|18,18,W,5|'
        obst_message = 'OBS|1,17,E,1|9,14,N,2|15,14,E,3|18,8,N,4|18,18,S,5|4,10,E,6|9,20,S,7|'
        rpi_flask = RPIFlaskServer(None)
        rpi_flask_process = Process(target=rpi_flask.run_server)
        rpi_flask_process.start()
        try:
            obstacles = parse_android_message(obst_message)
            cmd = await algo_process(obstacles)
            await translate_and_dispatch(cmd)

            # algo here
            # asyncio.run(app.execute())
            print("finished Task 1")
        except Exception as e:
            print(e)

    elif choice == 3:  # for testing only
        rpi.bluetooth_connect()
        rpi_flask = RPIFlaskServer(rpi)
        rpi_flask_process = Process(target=rpi_flask.run_server)
        rpi_flask_process.start()
    else:
        print("invalid choice")


def parse_android_message(message: str) -> List[dict]:
    obst_entries = message.split('|')[1:-1]
    obstacles = []
    for entry in obst_entries:
        x, y, d, obstacle_id = entry.split(',')
        x = int(x)
        y = int(y)
        obstacle_id = int(obstacle_id)
        if d == 'N':
            d = Direction.NORTH.value
        elif d == 'E':
            d = Direction.EAST.value
        elif d == 'S':
            d = Direction.SOUTH.value
        elif d == 'W':
            d = Direction.WEST.value
        obstacle = {'x': x, 'y': y, 'd': d, 'id': obstacle_id}
        obstacles.append(obstacle)

    return obstacles


if __name__ == '__main__':
    asyncio.run(main())
