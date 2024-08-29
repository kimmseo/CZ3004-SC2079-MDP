from enum import Enum
import serial as ser

'''
    SerialCmdBaseLL
    Base class for serial command low-level fns
    This is basically the inverse operation of the robot's Processor class
'''


class SerialCmdBaseLL:
    ser = None  # instance of serial.Serial
    CMD_LEN = 10
    ACK_TIMEOUT_MS =    200
    payload = ""
    is_reading = False

    class CmdChar(Enum):
        START_CHAR = b'x'
        CMD_CHAR = b'c'
        REQ_CHAR = b'q'
        MOTOR_CHAR = b'm'
        SENSOR_CHAR = b's'
        AUX_CHAR = b'a'
        END_CHAR = b'z'
        PAD_CHAR = b'.'

    class Modules(Enum):
        MOTOR = b'm'
        SENSOR = b's'
        AUX = b'a'

    class MotorCmd(Enum):
        FWD_CHAR = b'f'
        BWD_CHAR = b'b'
        RIGHT_CHAR = b'r'
        LEFT_CHAR = b'l'
        HALT_CHAR = b'h'
        CRAWL_CHAR = b'd'
        LINEAR_CHAR = b'j'
        T2_180_CHAR = b'!'
        T2_90_CHAR = b'?'
        T2_O1_CHAR = b'@'

    class SensorCmd(Enum):
        IR_LEFT = b'w'
        IR_RIGHT = b'e'
        USOUND = b'u'
        GZ = b'g'
        QTRN_YAW = b'y'
        QTRN_ALL = b'k'
        LAST_HALT = b'o'

    class KeyWord(Enum):
        WARN_OBSTACLE = "obst"

    def __init__(self, port, baud):
        self.ser = ser.Serial(port, baud)
        self.ser.timeout = self.ACK_TIMEOUT_MS / 1000
        pass

    def send_cmd(self) -> str:
        self.is_reading = True
        self.payload += self.CmdChar.END_CHAR.value
        if len(self.payload) != self.CMD_LEN:
            raise IOError("Command length is not correct")
        self.ser.flush()
        self.ser.flushInput()

        self.ser.write(self.payload)
        ret = self.ser.readline()
        ret = ret.replace(b'\x00', b'')
        # self.ser.flush()
        print("[LL] Sending command: " + str(self.payload))
        ret = bytes.decode(ret, 'utf-8')
        ret = ret.replace(str(self.KeyWord.WARN_OBSTACLE), '')
        self.is_reading = False
        return ret

    @staticmethod
    def ll_is_valid(ret) -> bool:
        if ret == "ack":
            return True
        else:
            return False

    def construct_cmd(self) -> None:
        self.payload = ""
        self.payload = self.CmdChar.START_CHAR.value

    def add_cmd_byte(self, is_cmd: bool) -> None:
        if is_cmd:
            self.payload += self.CmdChar.CMD_CHAR.value
        else:
            self.payload += self.CmdChar.REQ_CHAR.value

    def add_module_byte(self, module: Modules) -> None:
        self.payload += module.value

    def add_motor_cmd_byte(self, motor_cmd: MotorCmd) -> None:
        self.payload += motor_cmd.value

    def add_args_bytes(self, arg: int) -> None:
        # add speed but ensure it is 3 digits exactly
        arg_str = str(arg)
        if len(arg_str) > 3:
            raise IOError("Speed is too long")
        elif len(arg_str) < 3:
            arg_str = '0' * (3 - len(arg_str)) + arg_str
        self.payload += bytes(arg_str, 'utf-8')

    def add_sensor_byte(self, sensor_cmd: SensorCmd) -> None:
        self.payload += sensor_cmd.value

    def add_misc_byte(self, byte: bytes) -> None:
        self.payload += byte

    def pad_to_end(self) -> None:
        while len(self.payload) < self.CMD_LEN - 1:
            self.payload += self.CmdChar.PAD_CHAR.value
