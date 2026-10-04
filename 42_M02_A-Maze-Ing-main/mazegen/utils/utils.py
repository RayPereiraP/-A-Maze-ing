from enum import Enum


# --- ERRORS ---

class ConfigError(Exception):
    """Raised when the config file arguments are invalid."""


class MazeGenError(Exception):
    """Custom exception for maze generator errors"""


# --- DIRECTIONS ---

class Directions(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"


DIRECTIONS = {
    "N": 1,
    "E": 2,
    "S": 4,
    "W": 8
}


DIR_VECTORS = {
    "N": (0, -1),
    "S": (0, 1),
    "W": (-1, 0),
    "E": (1, 0),
}
