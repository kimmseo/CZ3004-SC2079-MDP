
from Cell import Cell
from Direction import Direction

class Robot:
    def __init__(self, x : int, y : int, direction : Direction):
        self.state = Cell(x, y, direction)

    def get_start_state(self):
        return self.state