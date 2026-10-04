from typing import Tuple


class Maze:
    """Fields already validated through MazeGenerator."""

    def __init__(
            self, width: int, height: int,
            entry: Tuple[int, int], exit: Tuple[int, int]
            ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid = [
            [
                {
                    "N": True,
                    "E": True,
                    "S": True,
                    "W": True,
                    "visited": False,
                    "pattern": False,
                }
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]

    # ------- Utility methods - maze ---------

    def get_cell(self, x: int, y: int) -> dict[str, bool]:
        """Return a cell dict at (x, y)."""

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError("Invalid cell")

        return self.grid[y][x]

    def get_neighbors(self, x: int, y: int) -> dict[str, tuple[int, int]]:
        """Return all valid neighbors of the (x, y) cell."""

        neighbors = {
            "N": (x, y-1),
            "E": (x+1, y),
            "S": (x, y+1),
            "W": (x-1, y)
        }

        valid = {}

        for d, coords in neighbors.items():
            try:
                self.get_cell(*coords)
                valid[d] = coords
            except ValueError:
                pass

        return valid
