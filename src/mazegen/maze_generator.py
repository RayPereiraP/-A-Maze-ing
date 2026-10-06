"""Maze generator: one class that builds, solves and writes a maze."""

from pathlib import Path
from typing import Optional, Union

from src.mazegen.generator import generate_perfect, open_loops
from src.mazegen.map import Map, Position
from src.mazegen.solver import shortest_path
from src.mazegen.writer import write_maze


class MazeGenerator:
    """Generate a maze from its size, entry, exit, mode and seed.

    Every position is (row, col), with (0, 0) at the top-left corner, the
    same convention as Map. The maze is generated when the object is
    created, and generate() builds it again.

    Example:
        generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19))
        print(generator.path)
        print(generator.maze_map.cell(0, 0).N)

    Attributes:
        rows: number of rows of the maze.
        cols: number of columns of the maze.
        entry: (row, col) of the entry.
        exit: (row, col) of the exit.
        perfect: True for a single path between any two cells, False for
            a board with loops.
        seed: the same seed always gives the same maze; None gives a
            different maze on each generation.
        maze_map: the generated structure, a Map of Cell objects.
        path: shortest path from the entry to the exit, as the letters
            "N", "S", "E" and "W".
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        entry: Position,
        exit: Position,
        perfect: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        """Store the parameters and generate the first maze.

        Raises:
            ValueError: if a dimension is smaller than 1, if the entry or
                the exit is outside the maze, or if they are the same cell.
        """
        if rows < 1 or cols < 1:
            raise ValueError("The maze needs at least 1 row and 1 column.")
        for name, (row, col) in (("entry", entry), ("exit", exit)):
            if not (0 <= row < rows and 0 <= col < cols):
                raise ValueError(f"The {name} must be inside the maze.")
        if entry == exit:
            raise ValueError("The entry and the exit must be different.")
        self.rows: int = rows
        self.cols: int = cols
        self.entry: Position = entry
        self.exit: Position = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.maze_map: Map
        self.path: str
        self.generate()

    def generate(self) -> None:
        """Build a new maze and its shortest path from the parameters.

        Replaces maze_map and path. With a seed the result is always the
        same maze; change the seed attribute first to get another one.
        """
        maze_map = Map(self.rows, self.cols, self.entry, self.exit)
        generate_perfect(maze_map, self.seed)
        if not self.perfect:
            open_loops(maze_map, self.seed)
        self.path = shortest_path(maze_map)
        self.maze_map = maze_map

    def write(self, filename: Union[str, Path]) -> None:
        """Write the maze, its entry, its exit and the path to a file.

        Raises:
            OSError: if the file cannot be written.
        """
        write_maze(self.maze_map, self.path, filename)
