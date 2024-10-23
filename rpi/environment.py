class Obstacle:
    def __init__(self, x, y, id, d):
        self.x = x
        self.y = y
        self.id = id
        self.d = d

    def to_dict(self):
        return {"x": self.x, "y": self.y, "id": self.id, "d": self.d}

class Environment:
    def __init__(self, size_x, size_y, robot_x, robot_y, robot_direction):
        self.obstacles = []
        self.retrying = False
        self.size_x = size_x
        self.size_y = size_y
        self.robot_x = robot_x
        self.robot_y = robot_y
        self.robot_direction = robot_direction

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def to_retry(self):
        self.retrying = True

    def to_dict(self):
        return {
            "obstacles": [obstacle.to_dict() for obstacle in self.obstacles],
            "retrying": self.retrying,
            "size_x": self.size_x,
            "size_y": self.size_y,
            "robot_x": self.robot_x,
            "robot_y": self.robot_y,
            "robot_direction": self.robot_direction,
        }
