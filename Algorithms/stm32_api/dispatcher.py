import asyncio
from asyncio import Task
from enum import Enum
from typing import Callable, Optional, List, Any

from stm32_api.robot_controller import RobotController, PinState

"""
This is a generic dispatcher that can be used to dispatch commands to the robot. It sends a given command for {
patience} times, with a inter-tx delay of {base}^i ms for each ith attempt. The n-ary exponential backoff is given by 
{base}^i which is clipped at the lower bound by the SerialCmdBaseLL.ACK_TIMEOUT_MS. 

This algorithm is used to help the robot recover from an unresponsive state, and to prevent the robot from being 
overwhelmed. It also offloads error handling from the user, and allows for a more robust and predictable command 
dispatching mechanism. 
"""


class _IO_Attr_Type(Enum):
    PHYSICAL = 0
    SIMULATED = 1


class _Dispatcher:
    MAXIMUM_BACKOFF_PERIOD_MS = 2500

    def __init__(self, robot: RobotController, patience: int, base: int = 2,
                 u_if: _IO_Attr_Type = _IO_Attr_Type.PHYSICAL):
        self.patience = patience  # num iterations
        self.base = base  # exponent base
        self.robot = robot  # instance of robot controller
        self.clip = lambda x, a, b: max(a, min(x, b))  # clip function
        self.p_sig_mv = robot.poll_is_moving
        self.p_sig_ob = robot.poll_obstruction
        if u_if is not _IO_Attr_Type.PHYSICAL:
            print("[DISPATCHER] IN SIMULATED I/O MODE")
            return
        if self.robot.obstr_pin_state is PinState.Z:
            raise IOError("[DISPATCHER] CRITICAL: OBSTACLE PIN IN HIGH IMPEDANCE STATE DURING INITIALIZATION AND "
                          "THEREFORE N/C")
        if self.robot.cmd_pin_state is PinState.Z:
            raise IOError("[DISPATCHER] CRITICAL: COMMAND PIN IN HIGH IMPEDANCE STATE DURING INITIALIZATION AND "
                          "THEREFORE N/C")

    async def _dispatcher(self, fn: Callable, args: List[Any], fn_sig_obst: Callable) -> Optional[Any]:
        for i in range(self.patience):
            backoff_period = self.clip(self.base ** i, self.robot.drv.ACK_TIMEOUT_MS, self.MAXIMUM_BACKOFF_PERIOD_MS)
            print("[DISPATCHER] Attempting to dispatch command to robot, attempt", i + 1, "of", self.patience,
                  " , with a delay of", backoff_period, "ms")
            #print(str(*args) + ",")
            #print(self.robot)
            x = fn(self.robot, *args)  # for python 3.7 compatibility
            if x not in [False, None]:
                print("[DISPATCHER] Command dispatched successfully!")
                return x
            if self.p_sig_ob and self.robot.obstr_pin_state is not PinState.Z:  # if obstruction detected, signal and exit task
                fn_sig_obst()
                return False
            if i >= self.patience - 1:
                break
            await asyncio.sleep(backoff_period / 1000)
        print("[DISPATCHER] Patience ran out, command not dispatched successfully!")
        return False

    """
    This function executes a function fn with arguments args and an optional callback function cb.
    """

    def dispatch(self, fn: Callable, args: List[Any], fn_sig_obst: Callable,
                 cb: Optional[Callable] = None) -> asyncio.Task:
        async def _i_cb_wrapper(task):
            result = task.result()
            if cb:
                if asyncio.iscoroutinefunction(cb):
                    await cb(result)
                else:
                    cb(result)

        h_tsk = asyncio.create_task(self._dispatcher(fn, args, fn_sig_obst))
        if cb is not None:
            h_tsk.add_done_callback(lambda t: asyncio.create_task(_i_cb_wrapper(t)))
        return h_tsk


    """
    This function executes a callback function which is given an argument corresponding to the magnitude of the last cmd
    executed, i.e. if cmd is move 100cm, and it moved 80cm, argument is 80.
    """

    def listen_for_obstruction(self, fn: Callable[..., None]) -> None:
        self.robot._inst_obstr_cb = fn



"""
Blocking version. MUST be awaited.
"""


class BlockingDispatcher(_Dispatcher):

    def __init__(self, robot: RobotController, patience: int, base: int = 2, u_if: _IO_Attr_Type = _IO_Attr_Type.PHYSICAL):
        super().__init__(robot, patience, base, u_if)

    async def dispatchB(self, fn: Callable, args: List[Any], fn_sig_obst: Callable) -> Any:
        return await asyncio.create_task(self._dispatcher(fn, args, fn_sig_obst))


"""
Concurrent version. Directly inherits from _Dispatcher.
"""


class ConcurrentDispatcher(_Dispatcher):

    def __init__(self, robot: RobotController, patience: int, base: int = 2, u_if: _IO_Attr_Type = _IO_Attr_Type.PHYSICAL):
        super().__init__(robot, patience, base, u_if)
