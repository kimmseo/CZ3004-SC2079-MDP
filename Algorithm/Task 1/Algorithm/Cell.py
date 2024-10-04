from Direction import Direction

class Cell:
    def __init__(self, x : int, y : int, direction : Direction = Direction.NORTH, screenshot_id : int = -1, penalty = 0):
        self.x = x
        self.y = y
        self.direction = direction
        self.screenshot_id = screenshot_id
        self.penalty = penalty

    def set_screenshot(self, id : int):
        self.screenshot_id = id

    def get_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "d": self.direction,
            "s": self.screenshot_id,
        }
    
    def is_eq(self, x, y, direction):
        """Compare given x, y, direction with cell state's position and direction

        Args:
            x (int): x coordinate
            y (int): y coordinate
            direction (Direction): direction of cell

        Returns:
            bool: True if same, False otherwise
        """
        return self.x == x and self.y == y and self.direction == direction