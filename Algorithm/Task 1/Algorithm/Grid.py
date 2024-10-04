import Constants

from Helpers import is_valid_coord
from typing import List
from Direction import Direction
from Obstacle import Obstacle
from Cell import Cell


class Grid:
    def __init__(self, width : int, height : int):
        self.width = width
        self.width  = height
        self.obstacles : List[Obstacle] = []
        
    def add_obstacle(self, obstacle : Obstacle):
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)

    def reachable(self, x : int, y : int, turn : bool = False, preTurn : bool = False) -> bool:
        if not is_valid_coord(x, y):
            return False
        
        for obstacle in self.obstacles:
            #Check if obstacle has a minimum distance of 4
            if (obstacle.x == 4 and obstacle.y <= 4 and x < 4 and y < 4) and (abs(obstacle.x - x) + abs(obstacle.y - y) >= 4):
                continue
            if turn and max(abs(obstacle.x - x), abs(obstacle.y - y)) < Constants.EXPANDED_CELL * 2 + 1:
                return False
            if preTurn and max(abs(obstacle.x - x), abs(obstacle.y - y)) < Constants.EXPANDED_CELL * 2 + 1:
                return False
            elif max(abs(obstacle.x - x), abs(obstacle.y - y)) < 2:
                return False
            
        return True
    
    def get_view_obstacle_positions(self) -> List[Cell]:
        positions = []
        for obstacle in self.obstacles:
            if obstacle.direction == Direction.SKIP:
                continue
            else:
                view_states = [view_state for view_state in obstacle.get_view_state() if self.reachable(view_state.x, view_state.y)]
            positions.append(view_states)

        return positions