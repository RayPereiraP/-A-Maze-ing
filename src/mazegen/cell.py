"""Maze cell: stores only the state of its own walls."""


class Cell:
    """A cell with four walls, a path marker and a "42" marker.

    For each wall, True means the wall is closed and False means it is open.
    The cell does not know where it is in the grid or who its neighbours are.
    """

    def __init__(self) -> None:
        """Create the cell closed, off the path and outside the "42"."""
        self.N: bool = True
        self.S: bool = True
        self.E: bool = True
        self.W: bool = True
        self.path: bool = False
        self.is_42: bool = False
