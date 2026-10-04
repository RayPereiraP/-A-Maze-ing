# ----- CONFIG KEYS -----

from enum import Enum


class Config(Enum):
    """
    Enum representing configuration-related constants for the maze project.

    Attributes:
        CONFIG (str): Default configuration file name.
        WIDTH (str): Key for maze width in the config file.
        HEIGHT (str): Key for maze height in the config file.
        ENTRY (str): Key for entry coordinates in the config file.
        EXIT (str): Key for exit coordinates in the config file.
        PERFECT (str): Key indicating whether the maze is perfect (no loops).
        OUTPUT_FILE (str): Key for the output filename of the generated maze.
    """

    CONFIG = "config.txt"

    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PERFECT = "PERFECT"
    OUTPUT_FILE = "OUTPUT_FILE"

    THEME = "THEME"
    PATTERN = "PATTERN"
    SEED = "SEED"

    # ALGORITHM = "ALGORITHM"
    # DISPLAY_MODE = "DISPLAY_MODE"


CONFIG = Config.CONFIG.value
WIDTH = Config.WIDTH.value
HEIGHT = Config.HEIGHT.value
ENTRY = Config.ENTRY.value
EXIT = Config.EXIT.value
OUTPUT_FILE = Config.OUTPUT_FILE.value
PERFECT = Config.PERFECT.value
SEED = Config.SEED.value
THEME = Config.THEME.value
PATTERN = Config.PATTERN.value

# ALGORITHM = Config.ALGORITHM.value
# DISPLAY_MODE = Config.DISPLAY_MODE.value
