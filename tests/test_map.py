"""Tests for Task 1 and Task 2: Cell, Map and the "42" pattern."""

import contextlib
import io
import unittest
from typing import Dict, List, Optional, Set, Tuple

from src.mazegen import Cell, Map


WALLS = ("N", "S", "E", "W")
Wall = Tuple[int, int, str]
State = Dict[Wall, bool]
Position = Tuple[int, int]


def build_map(
    rows: int,
    cols: int,
    entry: Optional[Position] = None,
    exit: Optional[Position] = None,
) -> Tuple[Map, str]:
    """Build a map and return it with what it printed to the console."""
    console = io.StringIO()
    with contextlib.redirect_stderr(console):
        maze_map = Map(rows, cols, entry, exit)
    return maze_map, console.getvalue()


def marked_42(maze_map: Map) -> Set[Position]:
    """Collect the positions of the cells that belong to the "42"."""
    return {
        (row, col)
        for row in range(maze_map.rows)
        for col in range(maze_map.cols)
        if maze_map.cell(row, col).is_42
    }


def wall_state(maze_map: Map) -> State:
    """Snapshot every wall of the map, keyed by (row, col, wall)."""
    return {
        (row, col, wall): getattr(maze_map.cell(row, col), wall)
        for row in range(maze_map.rows)
        for col in range(maze_map.cols)
        for wall in WALLS
    }


def changed_walls(before: State, after: State) -> List[Wall]:
    """List the walls whose value changed between two snapshots."""
    return sorted(key for key in before if before[key] != after[key])


class TestCell(unittest.TestCase):
    """Initial state and isolation of Cell."""

    def test_initial_state(self) -> None:
        cell = Cell()
        for wall in WALLS:
            self.assertIs(getattr(cell, wall), True)
        self.assertIs(cell.path, False)
        self.assertIs(cell.is_42, False)

    def test_does_not_know_position(self) -> None:
        self.assertEqual(
            sorted(vars(Cell())), ["E", "N", "S", "W", "is_42", "path"]
        )


class TestMap(unittest.TestCase):
    """Dimensions, access and wall opening of Map."""

    def test_dimensions(self) -> None:
        maze_map = Map(3, 5)
        self.assertEqual(len(maze_map.grid), 3)
        for row in maze_map.grid:
            self.assertEqual(len(row), 5)
            for cell in row:
                self.assertIsInstance(cell, Cell)

    def test_cells_are_independent(self) -> None:
        maze_map = Map(3, 5)
        unique = {id(cell) for row in maze_map.grid for cell in row}
        self.assertEqual(len(unique), 15)

    def test_invalid_dimensions(self) -> None:
        for rows, cols in ((0, 5), (5, 0), (-1, 3)):
            with self.assertRaises(ValueError):
                Map(rows, cols)

    def test_access_by_position(self) -> None:
        maze_map = Map(3, 5)
        self.assertIs(maze_map.cell(2, 4), maze_map.grid[2][4])

    def test_access_outside_grid(self) -> None:
        maze_map = Map(3, 5)
        for row, col in ((-1, 0), (0, -1), (3, 0), (0, 5)):
            with self.assertRaises(IndexError):
                maze_map.cell(row, col)

    def test_open_in_four_directions(self) -> None:
        # direction -> (neighbour position from (1, 1), opposite wall)
        cases = {
            "N": ((0, 1), "S"),
            "S": ((2, 1), "N"),
            "E": ((1, 2), "W"),
            "W": ((1, 0), "E"),
        }
        for direction, (neighbour, opposite) in cases.items():
            with self.subTest(direction=direction):
                maze_map = Map(3, 3)
                before = wall_state(maze_map)
                self.assertIs(maze_map.open_wall(1, 1, direction), True)
                after = wall_state(maze_map)
                expected = sorted([(1, 1, direction), (*neighbour, opposite)])
                self.assertEqual(changed_walls(before, after), expected)
                self.assertIs(getattr(maze_map.cell(1, 1), direction), False)
                self.assertIs(
                    getattr(maze_map.cell(*neighbour), opposite), False
                )

    def test_open_towards_border(self) -> None:
        cases = (
            (0, 1, "N"),
            (2, 1, "S"),
            (1, 2, "E"),
            (1, 0, "W"),
        )
        for row, col, direction in cases:
            with self.subTest(direction=direction):
                maze_map = Map(3, 3)
                before = wall_state(maze_map)
                self.assertIs(maze_map.open_wall(row, col, direction), False)
                self.assertEqual(before, wall_state(maze_map))

    def test_open_does_not_mark_path(self) -> None:
        maze_map = Map(2, 2)
        maze_map.open_wall(0, 0, "E")
        for row in maze_map.grid:
            for cell in row:
                self.assertIs(cell.path, False)

    def test_invalid_direction(self) -> None:
        maze_map = Map(3, 3)
        before = wall_state(maze_map)
        for direction in ("X", "n", "", "path"):
            with self.assertRaises(ValueError):
                maze_map.open_wall(1, 1, direction)
        self.assertEqual(before, wall_state(maze_map))

    def test_origin_outside_grid(self) -> None:
        maze_map = Map(3, 3)
        with self.assertRaises(IndexError):
            maze_map.open_wall(3, 0, "N")


class TestPattern42(unittest.TestCase):
    """Marking and omission of the "42" pattern in Map.__init__."""

    # The "42" centred in a 9x11 map: one free cell on every side.
    CENTRED_9X11 = (
        "...........",
        "...........",
        "..#.#.###..",
        "..#.#...#..",
        "..###.###..",
        "....#.#....",
        "....#.###..",
        "...........",
        "...........",
    )

    def expected_9x11(self) -> Set[Position]:
        return {
            (row, col)
            for row, line in enumerate(self.CENTRED_9X11)
            for col, char in enumerate(line)
            if char == "#"
        }

    def test_marks_centred_pattern(self) -> None:
        maze_map, console = build_map(9, 11, entry=(0, 0), exit=(8, 10))
        self.assertEqual(marked_42(maze_map), self.expected_9x11())
        self.assertEqual(console, "")

    def test_marks_without_entry_and_exit(self) -> None:
        maze_map, console = build_map(9, 11)
        self.assertEqual(marked_42(maze_map), self.expected_9x11())
        self.assertEqual(console, "")

    def test_smallest_map_that_fits(self) -> None:
        maze_map, console = build_map(7, 9)
        self.assertEqual(len(marked_42(maze_map)), 20)
        self.assertEqual(console, "")

    def test_too_small_omits_pattern(self) -> None:
        for rows, cols in ((6, 9), (7, 8), (3, 3), (1, 50), (50, 1)):
            with self.subTest(rows=rows, cols=cols):
                maze_map, console = build_map(rows, cols)
                self.assertEqual(marked_42(maze_map), set())
                self.assertIn("too small", console)

    def test_entry_on_pattern_omits_pattern(self) -> None:
        maze_map, console = build_map(9, 11, entry=(2, 2), exit=(8, 10))
        self.assertEqual(marked_42(maze_map), set())
        self.assertIn("entry or the exit", console)

    def test_exit_on_pattern_omits_pattern(self) -> None:
        maze_map, console = build_map(9, 11, entry=(0, 0), exit=(6, 8))
        self.assertEqual(marked_42(maze_map), set())
        self.assertIn("entry or the exit", console)

    def test_entry_in_gap_of_pattern_keeps_pattern(self) -> None:
        # (2, 3) is inside the drawing area but is not a cell of the "42".
        maze_map, console = build_map(9, 11, entry=(2, 3), exit=(8, 10))
        self.assertEqual(marked_42(maze_map), self.expected_9x11())
        self.assertEqual(console, "")

    def test_pattern_does_not_touch_walls_or_path(self) -> None:
        maze_map, _ = build_map(9, 11)
        for row in maze_map.grid:
            for cell in row:
                self.assertIs(cell.path, False)
                for wall in WALLS:
                    self.assertIs(getattr(cell, wall), True)


if __name__ == "__main__":
    unittest.main()
