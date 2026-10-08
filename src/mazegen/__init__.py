"""Reusable maze generation module.

Example:
    from mazegen import MazeGenerator

    generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19), seed=42)
    print(generator.path)                    # shortest path, as N/E/S/W
    print(generator.maze_map.cell(0, 0).N)   # True if that wall is closed

Every position is (row, col), with (0, 0) at the top-left corner. The
README of the package describes the parameters and the structure.
"""

from .cell import Cell
from .generator import generate_perfect, open_loops
from .map import Map
from .maze_generator import MazeGenerator
from .solver import shortest_path
from .writer import write_maze

__all__ = [
    "Cell",
    "Map",
    "MazeGenerator",
    "generate_perfect",
    "open_loops",
    "shortest_path",
    "write_maze",
]
