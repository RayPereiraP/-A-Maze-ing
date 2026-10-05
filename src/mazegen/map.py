"""Maze map: the grid of cells and the neighbourhood rules."""

import sys
from typing import Dict, List, Optional, Tuple

from src.mazegen.cell import Cell


Position = Tuple[int, int]

# direction -> (row change, column change, opposite wall)
DIRECTIONS: Dict[str, Tuple[int, int, str]] = {
    "N": (-1, 0, "S"),
    "S": (1, 0, "N"),
    "E": (0, 1, "W"),
    "W": (0, -1, "E"),
}

# Drawing of the "42": "#" is a cell of the pattern, "." is a normal cell.
# This is the only place that defines the size and shape of the drawing.
PATTERN_42: Tuple[str, ...] = (
    "#.#.###",
    "#.#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)
# Free cells required between the drawing and each border of the map.
PATTERN_42_MARGIN: int = 1


class Map:
    """Grid of cells; the only one that knows positions and neighbours.

    A cell position is always (row, col), with (0, 0) at the top-left corner.
    The row grows towards the south and the column towards the east.
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        entry: Optional[Position] = None,
        exit: Optional[Position] = None,
    ) -> None:
        """Create the grid with rows x cols new cells and mark the "42".

        Args:
            rows: number of rows in the grid.
            cols: number of columns in the grid.
            entry: (row, col) of the maze entry, if already known.
            exit: (row, col) of the maze exit, if already known.

        Raises:
            ValueError: if either dimension is smaller than 1.
        """
        if rows < 1 or cols < 1:
            raise ValueError("The map needs at least 1 row and 1 column.")
        self.rows: int = rows
        self.cols: int = cols
        self.grid: List[List[Cell]] = [
            [Cell() for _ in range(cols)] for _ in range(rows)
        ]
        self.entry: Optional[Position] = entry
        self.exit: Optional[Position] = exit
        self._mark_42()

    def _mark_42(self) -> None:
        """Mark the cells that draw the "42" in the centre of the map.

        The drawing is all or nothing: if the map is too small, or if the
        entry or the exit sits on the drawing, no cell is marked and an
        error message is printed instead.
        """
        height = len(PATTERN_42)
        width = len(PATTERN_42[0])
        if (
            self.rows < height + 2 * PATTERN_42_MARGIN
            or self.cols < width + 2 * PATTERN_42_MARGIN
        ):
            print(
                'Error: the maze is too small for the "42" pattern; '
                "pattern omitted.",
                file=sys.stderr,
            )
            return
        top = (self.rows - height) // 2
        left = (self.cols - width) // 2
        positions: List[Position] = [
            (top + row, left + col)
            for row in range(height)
            for col in range(width)
            if PATTERN_42[row][col] == "#"
        ]
        if self.entry in positions or self.exit in positions:
            print(
                'Error: the entry or the exit is on the "42" pattern; '
                "pattern omitted.",
                file=sys.stderr,
            )
            return
        for row, col in positions:
            self.grid[row][col].is_42 = True

    def contains(self, row: int, col: int) -> bool:
        """Tell whether the position (row, col) exists in the grid."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def cell(self, row: int, col: int) -> Cell:
        """Return the cell at position (row, col).

        Raises:
            IndexError: if the position is outside the grid.
        """
        if not self.contains(row, col):
            raise IndexError(f"Position ({row}, {col}) is outside the map.")
        return self.grid[row][col]

    def open_wall(self, row: int, col: int, direction: str) -> bool:
        """Open the wall between the cell (row, col) and its neighbour.

        Changes both cells: the `direction` wall of the origin and the
        opposite wall of the neighbour. If the neighbour is outside the grid
        (border), nothing is changed.

        Args:
            row: row of the origin cell.
            col: column of the origin cell.
            direction: one of the letters "N", "S", "E" or "W".

        Returns:
            True if the wall was opened, False if the direction points
            outside the grid.

        Raises:
            ValueError: if the direction is not one of the four letters.
            IndexError: if the origin cell is outside the grid.
        """
        if direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction!r}.")
        origin = self.cell(row, col)
        row_delta, col_delta, opposite = DIRECTIONS[direction]
        neighbour_row = row + row_delta
        neighbour_col = col + col_delta
        if not self.contains(neighbour_row, neighbour_col):
            return False
        neighbour = self.grid[neighbour_row][neighbour_col]
        setattr(origin, direction, False)
        setattr(neighbour, opposite, False)
        return True
