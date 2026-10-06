"""Tests for Task 4: shortest path from the entry to the exit."""

import contextlib
import io
import unittest
from typing import List, Optional, Set, Tuple

from src.mazegen import Map, generate_perfect, shortest_path
from src.mazegen.map import DIRECTIONS


Position = Tuple[int, int]

# (rows, cols, entry, exit); the first two are big enough for the "42".
SIZES: Tuple[Tuple[int, int, Position, Position], ...] = (
    (15, 20, (0, 0), (14, 19)),
    (7, 9, (6, 8), (0, 0)),
    (7, 5, (0, 0), (6, 4)),
    (1, 8, (0, 7), (0, 0)),
)


def build_map(
    rows: int,
    cols: int,
    entry: Optional[Position] = None,
    exit: Optional[Position] = None,
) -> Map:
    """Build a map with every wall closed, hiding its console messages."""
    with contextlib.redirect_stderr(io.StringIO()):
        return Map(rows, cols, entry, exit)


def walk(maze_map: Map, start: Position, letters: str) -> List[Position]:
    """Follow the letters from start; fail if a step crosses a wall."""
    visited: List[Position] = [start]
    row, col = start
    for letter in letters:
        if getattr(maze_map.cell(row, col), letter):
            raise AssertionError(
                f"Step {letter} from ({row}, {col}) hits a wall."
            )
        row_delta, col_delta, _ = DIRECTIONS[letter]
        row, col = row + row_delta, col + col_delta
        visited.append((row, col))
    return visited


def marked_path(maze_map: Map) -> Set[Position]:
    """Collect the positions of the cells marked as path."""
    return {
        (row, col)
        for row in range(maze_map.rows)
        for col in range(maze_map.cols)
        if maze_map.cell(row, col).path
    }


def two_routes_map() -> Map:
    """Build a 3x3 map with a 2-step and a 4-step route to the exit.

    The entry is (0, 0) and the exit is (0, 2). The short route is the top
    row; the long one goes down, along the middle row and back up.
    """
    maze_map = build_map(3, 3, entry=(0, 0), exit=(0, 2))
    for row, col, direction in (
        (0, 0, "E"), (0, 1, "E"),
        (0, 0, "S"), (1, 0, "E"), (1, 1, "E"), (1, 2, "N"),
    ):
        maze_map.open_wall(row, col, direction)
    return maze_map


class TestShortestPath(unittest.TestCase):
    """Validity, shortness and marking of the path."""

    def test_letters_lead_from_entry_to_exit(self) -> None:
        for rows, cols, entry, exit in SIZES:
            for seed in range(5):
                with self.subTest(rows=rows, cols=cols, seed=seed):
                    maze_map = build_map(rows, cols, entry, exit)
                    generate_perfect(maze_map, seed)
                    letters = shortest_path(maze_map)
                    self.assertLessEqual(set(letters), set("NSEW"))
                    visited = walk(maze_map, entry, letters)
                    self.assertEqual(visited[-1], exit)
                    # A shortest path never visits the same cell twice.
                    self.assertEqual(len(set(visited)), len(visited))

    def test_takes_the_shorter_of_two_routes(self) -> None:
        self.assertEqual(shortest_path(two_routes_map()), "EE")

    def test_takes_the_only_route(self) -> None:
        maze_map = build_map(2, 2, entry=(0, 0), exit=(0, 1))
        for row, col, direction in ((0, 0, "S"), (1, 0, "E"), (1, 1, "N")):
            maze_map.open_wall(row, col, direction)
        self.assertEqual(shortest_path(maze_map), "SEN")

    def test_marks_exactly_the_cells_of_the_path(self) -> None:
        maze_map = build_map(15, 20, (0, 0), (14, 19))
        generate_perfect(maze_map, 42)
        letters = shortest_path(maze_map)
        self.assertEqual(
            marked_path(maze_map), set(walk(maze_map, (0, 0), letters))
        )

    def test_second_call_clears_old_marks(self) -> None:
        maze_map = two_routes_map()
        maze_map.cell(2, 2).path = True
        shortest_path(maze_map)
        self.assertEqual(marked_path(maze_map), {(0, 0), (0, 1), (0, 2)})

    def test_does_not_change_walls_or_42(self) -> None:
        maze_map = build_map(15, 20, (0, 0), (14, 19))
        generate_perfect(maze_map, 42)

        def snapshot() -> List[Tuple[bool, bool, bool, bool, bool]]:
            return [
                (cell.N, cell.S, cell.E, cell.W, cell.is_42)
                for row in maze_map.grid
                for cell in row
            ]

        before = snapshot()
        shortest_path(maze_map)
        self.assertEqual(before, snapshot())

    def test_entry_equal_to_exit(self) -> None:
        maze_map = build_map(3, 3, entry=(1, 1), exit=(1, 1))
        self.assertEqual(shortest_path(maze_map), "")
        self.assertEqual(marked_path(maze_map), {(1, 1)})

    def test_missing_entry_or_exit(self) -> None:
        for entry, exit in ((None, (0, 1)), ((0, 0), None), (None, None)):
            with self.subTest(entry=entry, exit=exit):
                with self.assertRaises(ValueError):
                    shortest_path(build_map(2, 2, entry, exit))

    def test_unreachable_exit(self) -> None:
        maze_map = build_map(2, 2, entry=(0, 0), exit=(1, 1))
        maze_map.open_wall(0, 0, "E")
        with self.assertRaises(ValueError):
            shortest_path(maze_map)
        self.assertEqual(marked_path(maze_map), set())


if __name__ == "__main__":
    unittest.main()
