"""Tests for Task 3: perfect maze generation with a seed."""

import contextlib
import io
import unittest
from typing import List, Optional, Set, Tuple

from src.mazegen import Map, generate_perfect
from src.mazegen.map import DIRECTIONS


Position = Tuple[int, int]

# (rows, cols, entry, exit); the first two are big enough for the "42".
SIZES: Tuple[Tuple[int, int, Position, Position], ...] = (
    (15, 20, (0, 0), (14, 19)),
    (7, 9, (6, 8), (0, 0)),
    (5, 5, (0, 0), (4, 4)),
    (1, 8, (0, 0), (0, 7)),
    (1, 1, (0, 0), (0, 0)),
)


def build_maze(
    rows: int,
    cols: int,
    entry: Optional[Position] = None,
    exit: Optional[Position] = None,
    seed: Optional[int] = 42,
) -> Map:
    """Build a map (hiding its console messages) and generate the maze."""
    with contextlib.redirect_stderr(io.StringIO()):
        maze_map = Map(rows, cols, entry, exit)
    generate_perfect(maze_map, seed)
    return maze_map


def positions(maze_map: Map) -> List[Position]:
    """List every position of the map."""
    return [
        (row, col)
        for row in range(maze_map.rows)
        for col in range(maze_map.cols)
    ]


def free_cells(maze_map: Map) -> Set[Position]:
    """Collect the positions that are not part of the "42"."""
    return {
        pos for pos in positions(maze_map) if not maze_map.cell(*pos).is_42
    }


def reachable(maze_map: Map, start: Position) -> Set[Position]:
    """Collect the positions reached from start by walking open walls."""
    seen: Set[Position] = {start}
    pending: List[Position] = [start]
    while pending:
        row, col = pending.pop()
        for direction, (row_delta, col_delta, _) in DIRECTIONS.items():
            neighbour = (row + row_delta, col + col_delta)
            if getattr(maze_map.cell(row, col), direction):
                continue
            if neighbour not in seen:
                seen.add(neighbour)
                pending.append(neighbour)
    return seen


def count_passages(maze_map: Map) -> int:
    """Count the open walls between two cells, each one once."""
    return sum(
        1
        for row, col in positions(maze_map)
        for direction in ("S", "E")
        if not getattr(maze_map.cell(row, col), direction)
    )


def wall_snapshot(maze_map: Map) -> List[Tuple[bool, bool, bool, bool]]:
    """Copy the four walls of every cell, in reading order."""
    return [
        (cell.N, cell.S, cell.E, cell.W)
        for row in maze_map.grid
        for cell in row
    ]


class TestGeneratePerfect(unittest.TestCase):
    """Connectivity, absence of loops, closed cells and the seed."""

    def test_every_free_cell_is_reachable(self) -> None:
        for rows, cols, entry, exit in SIZES:
            with self.subTest(rows=rows, cols=cols):
                maze_map = build_maze(rows, cols, entry, exit)
                self.assertEqual(
                    reachable(maze_map, entry), free_cells(maze_map)
                )

    def test_has_no_loops(self) -> None:
        # Connected cells with exactly (cells - 1) passages form a tree.
        for rows, cols, entry, exit in SIZES:
            with self.subTest(rows=rows, cols=cols):
                maze_map = build_maze(rows, cols, entry, exit)
                self.assertEqual(
                    count_passages(maze_map), len(free_cells(maze_map)) - 1
                )

    def test_42_cells_stay_closed(self) -> None:
        maze_map = build_maze(15, 20, (0, 0), (14, 19))
        cells_42 = [
            maze_map.cell(*pos)
            for pos in positions(maze_map)
            if maze_map.cell(*pos).is_42
        ]
        self.assertEqual(len(cells_42), 20)
        for cell in cells_42:
            self.assertEqual((cell.N, cell.S, cell.E, cell.W), (True,) * 4)

    def test_borders_stay_closed(self) -> None:
        for rows, cols, entry, exit in SIZES:
            with self.subTest(rows=rows, cols=cols):
                maze_map = build_maze(rows, cols, entry, exit)
                for col in range(cols):
                    self.assertIs(maze_map.cell(0, col).N, True)
                    self.assertIs(maze_map.cell(rows - 1, col).S, True)
                for row in range(rows):
                    self.assertIs(maze_map.cell(row, 0).W, True)
                    self.assertIs(maze_map.cell(row, cols - 1).E, True)

    def test_neighbours_agree_on_shared_wall(self) -> None:
        maze_map = build_maze(15, 20, (0, 0), (14, 19))
        for row, col in positions(maze_map):
            cell = maze_map.cell(row, col)
            if row + 1 < maze_map.rows:
                self.assertIs(cell.S, maze_map.cell(row + 1, col).N)
            if col + 1 < maze_map.cols:
                self.assertIs(cell.E, maze_map.cell(row, col + 1).W)

    def test_same_seed_gives_same_maze(self) -> None:
        first = build_maze(15, 20, (0, 0), (14, 19), seed=7)
        second = build_maze(15, 20, (0, 0), (14, 19), seed=7)
        self.assertEqual(wall_snapshot(first), wall_snapshot(second))

    def test_different_seeds_give_different_mazes(self) -> None:
        first = build_maze(15, 20, (0, 0), (14, 19), seed=1)
        second = build_maze(15, 20, (0, 0), (14, 19), seed=2)
        self.assertNotEqual(wall_snapshot(first), wall_snapshot(second))

    def test_works_without_seed_and_without_entry(self) -> None:
        maze_map = build_maze(9, 11, seed=None)
        self.assertEqual(reachable(maze_map, (0, 0)), free_cells(maze_map))
        self.assertEqual(
            count_passages(maze_map), len(free_cells(maze_map)) - 1
        )

    def test_does_not_mark_path_or_change_42(self) -> None:
        before = build_maze(15, 20, (0, 0), (14, 19))
        with contextlib.redirect_stderr(io.StringIO()):
            untouched = Map(15, 20, (0, 0), (14, 19))
        for pos in positions(before):
            self.assertIs(before.cell(*pos).path, False)
            self.assertIs(before.cell(*pos).is_42, untouched.cell(*pos).is_42)


if __name__ == "__main__":
    unittest.main()
