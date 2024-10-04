import Constants

def is_valid_coord(x : int, y : int):
    return x >= 0 and x < Constants.WIDTH - 1  and y >= 0 and y < Constants.HEIGHT - 1