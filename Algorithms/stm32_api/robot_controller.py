from asyncio import Task
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any
import asyncio
import serial as ser
from stm32_api.serial_cmd_base_ll import SerialCmdBaseLL

import RPi.GPIO as GPIO

'''
Python API that abstracts away the low-level serial communication with the robot.
Users are expected to handle general exceptions, such as IOError, ValueError, etc.
Additionally, None or False is returned if the command was not attended to by the robot.

DMA buffer flushing is handled on the robot side, DO NOT spam commands at intervals less
than 20ms. It will auto recover from unresponsive state within 20ms.

Commands that are ack-ed are guaranteed to be executed (as this means that the robot has internally
delegated the task to the motor controller thread).
unless an overriding command is sent OR the robot overrides it. 
For instance, an obstacle is detected while forward cmd is given.

It is recommended to space out commands. If not, the robot will queue up to 10 commands, and execute 
them sequentially. The resulting motion is less predicable.

Requests are generally cheaper than commands, and can be assumed to return within ACK_TIMEOUT_MS.

'''


class PinState(Enum):
    HIGH = 1
    LOW = 0
    Z = -1


class RobotController:
    drv = None  # instance of serial_cmd_base_ll
    _inst_obstr_cb = None  # obstacle callback

    PIN_COMMAND = 15
    PIN_OBSTACLE = 14

    def __init__(self, port, baudrate, _inst_obstr_cb: Optional[Callable[..., None]] = None):
        self.drv = SerialCmdBaseLL(port, baudrate)
        GPIO.setmode(GPIO.BCM)
        self.cmd_pin_state = PinState.Z
        self.obstr_pin_state = PinState.Z

        GPIO.setup(self.PIN_COMMAND, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # LED pin set as output
        GPIO.setup(self.PIN_OBSTACLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # PWM pin set as output
        if GPIO.input(self.PIN_COMMAND) == GPIO.HIGH:
            print("[CONTROLLER] WARN: COMMAND PIN N/C OR UNEXPECTED STATE")
        else:
            self.cmd_pin_state = PinState.LOW

        if GPIO.input(self.PIN_OBSTACLE) == GPIO.HIGH:
            print("[CONTROLLER] WARN: OBSTACLE PIN N/C OR UNEXPECTED STATE")
        else:
            self.obstr_pin_state = PinState.LOW
        self._inst_obstr_cb = _inst_obstr_cb
        if self._inst_obstr_cb is not None:
            GPIO.add_event_detect(self.PIN_OBSTACLE, GPIO.RISING,
                                  callback=self.sig_obst_callback, bouncetime=50)


    '''
    Command robot to move forward/backward by [dist] cm.
    0 <= dist <= 999
    999 is interpreted as "move forward until obstacle detected".
    returns True if command was acknowledged, False otherwise.
    '''

    def move_forward(self, dist: int, no_brakes: bool = False) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-999")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.FWD_CHAR)
        self.drv.add_args_bytes(dist)
        self.drv.add_motor_cmd_byte(self.drv.CmdChar.PAD_CHAR) #empty
        if no_brakes:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LINEAR_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def move_backward(self, dist: int, no_brakes: bool = False) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-999")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.BWD_CHAR)
        self.drv.add_args_bytes(dist)
        self.drv.add_motor_cmd_byte(self.drv.CmdChar.PAD_CHAR) #empty
        if no_brakes:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LINEAR_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    '''
    Command robot to turn left/right by [angle] degrees and in the direction specified by [dir].
    0 <= angle <= 359
    dir = True means turn forward, dir = False means turn backward.
    returns True if command was acknowledged, False otherwise.
    '''

    def turn_left(self, angle: int, dir: bool, no_brakes: bool = False) -> bool:
        if angle < 0 or angle > 359:
            raise ValueError("Invalid angle, must be 0-359")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LEFT_CHAR)
        self.drv.add_args_bytes(angle)
        if dir:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.FWD_CHAR)
        else:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.BWD_CHAR)

        if no_brakes:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LINEAR_CHAR)

        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def turn_right(self, angle: int, dir: bool, no_brakes: bool = False) -> bool:
        if angle < 0 or angle > 359:
            raise ValueError("Invalid angle, must be 0-359")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.RIGHT_CHAR)
        self.drv.add_args_bytes(angle)
        if dir:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.FWD_CHAR)
        else:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.BWD_CHAR)

        if no_brakes:
            self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LINEAR_CHAR)

        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    '''
    Requests the quaternion vector a + bi + cj + dk,
    which are computed from accel/gyro data.
    '''

    def get_quaternion(self) -> Optional[list]:
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.QTRN_ALL)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()

        ret = ret.split(';')
        ret = [x.strip() for x in ret]
        if len(ret) != 4:
            return None
        try:
            ret = [float(x) for x in ret]
        except ValueError:
            return None
        return ret

    '''
    Requests the gyroscope Z axis angular velocity in degrees per second.
    '''

    def get_gyro_Z(self) -> Optional[float]:
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.GZ)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()
        try:
            ret = float(ret)
        except ValueError:
            return None
        return ret

    '''
    Requests the yaw angle in degrees, which is given by
    arctan(2*(q0*q3 + q1*q2), 1 - 2*(q2^2 + q3^2)).
    '''

    def get_yaw(self) -> Optional[float]:
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.QTRN_YAW)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()
        try:
            ret = float(ret)
        except ValueError:
            return None
        return ret

    '''
    Requests the left/right cm-approximation derived from the reflected IR illuminance,
    given by the formula where x is the analog signal in mV.
    
    Note that this measurement is not very accurate and is dependent on the surface reflectance.
    '''

    def get_ir_L(self) -> Optional[float]:
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_LEFT)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()
        try:
            ret = float(ret)
        except ValueError:
            return None
        return ret

    def get_ir_R(self) -> Optional[float]:
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_RIGHT)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()
        try:
            ret = float(ret)
        except ValueError:
            return None
        return ret

    def set_threshold_stop_distance_left(self, dist: int) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-999")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_LEFT)
        self.drv.add_args_bytes(dist)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def set_threshold_stop_distance_right(self, dist: int) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-998")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_RIGHT)
        self.drv.add_args_bytes(dist)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def set_threshold_disable_obstacle_detection_left(self) -> bool:

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_LEFT)
        self.drv.add_args_bytes(999)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def set_threshold_disable_obstacle_detection_right(self) -> bool:

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.SENSOR)
        self.drv.add_sensor_byte(self.drv.SensorCmd.IR_RIGHT)
        self.drv.add_args_bytes(999)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())



    """ DEPRECIATED: USE BELOW INSTEAD
    async def listen_for_obstruction(self, callback: Callable[..., None]):
        self._inst_obstr_cb = callback
        print("running")

        while True:
            if not self.drv.is_reading and self.drv.ser.in_waiting > 0:

                line = self.drv.ser.readline().decode('utf-8')

                self.drv.ser.flush()
                print(line)

                if str(self.drv.KeyWord.WARN_OBSTACLE.value) in line:
                    self._inst_obstr_cb()
            await asyncio.sleep(0.01)
    """

    def sig_obst_callback(self, channel):

        if self._inst_obstr_cb is not None:
            _d_ret = self.get_last_successful_arg()
            self._inst_obstr_cb(_d_ret)
    def poll_obstruction(self):
        return GPIO.input(self.PIN_OBSTACLE)

    def poll_is_moving(self):
        return GPIO.input(self.PIN_COMMAND)

    def halt(self):
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_sensor_byte(self.drv.MotorCmd.HALT_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def crawl_forward(self, dist: int) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-999")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.FWD_CHAR)
        self.drv.add_args_bytes(dist)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.CRAWL_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def crawl_backward(self, dist: int) -> bool:
        if dist < 0 or dist > 999:
            raise ValueError("Invalid distance, must be 0-999")

        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.MOTOR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.BWD_CHAR)
        self.drv.add_args_bytes(dist)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.CRAWL_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())


    def get_last_successful_arg(self):
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(False)
        self.drv.add_module_byte(self.drv.Modules.AUX)
        self.drv.add_sensor_byte(self.drv.SensorCmd.LAST_HALT)
        self.drv.pad_to_end()
        ret = self.drv.send_cmd()
        try:
            ret = float(ret)
        except ValueError:
            return None
        return ret

    def T2_180(self, dir: bool):
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.AUX)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.T2_180_CHAR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LEFT_CHAR) if dir else self.drv.add_motor_cmd_byte(self.drv.MotorCmd.RIGHT_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def T2_90(self, dir: bool):
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.AUX)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.T2_90_CHAR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LEFT_CHAR) if dir else self.drv.add_motor_cmd_byte(self.drv.MotorCmd.RIGHT_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

    def T2_O1(self, dir: bool):
        self.drv.construct_cmd()
        self.drv.add_cmd_byte(True)
        self.drv.add_module_byte(self.drv.Modules.AUX)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.T2_O1_CHAR)
        self.drv.add_motor_cmd_byte(self.drv.MotorCmd.LEFT_CHAR) if dir else self.drv.add_motor_cmd_byte(self.drv.MotorCmd.RIGHT_CHAR)
        self.drv.pad_to_end()
        return self.drv.ll_is_valid(self.drv.send_cmd())

