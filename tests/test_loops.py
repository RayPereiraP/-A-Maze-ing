"""Tests for Task 6: the non-perfect mode (PERFECT=False)."""

import unittest
from typing import List, Optional, Tuple

from src.mazegen import Map, open_loops, shortest_path
from src.mazegen.map import DIRECTIONS
from tests.test_generator import (
    build_maze,
    count_passages,
    free_cells,
    positions,
    reachable,
    wall_snapshot,
)
from tests.test_solver import build_map, walk


Position = Tuple[int, int]

# (rows, cols, entry, exit); the first three are big enough for the "42".
SIZES: Tuple[Tuple[int, int, Position, Position], ...] = (
    (15, 20, (0, 0), (14, 19)),
    (20, 15, (19, 0), (0, 14)),
    (7, 9, (6, 8), (0, 0)),
    (7, 5, (0, 0), (6, 4)),
    (4, 4, (0, 0), (3, 3)),
)
SEEDS = range(10)


def build_board(
    rows: int,
    cols: int,
    entry: Optional[Position] = None,
    exit: Optional[Position] = None,
    seed: Optional[int] = 42,
) -> Map:
    """Build a perfect maze and open its extra loops, with one seed."""
    maze_map = build_maze(rows, cols, entry, exit, seed)
    open_loops(maze_map, seed)
    return maze_map


def count_loops(maze_map: Map) -> int:
    """Count the independent loops: passages - cells + 1."""
    return count_passages(maze_map) - len(free_cells(maze_map)) + 1


def real_dead_ends(maze_map: Map) -> List[Position]:
    """List the dead-ends that still have a wall that could be opened.

    A dead-end closed in by the border and the "42" is not listed: no wall
    of it leads to a normal cell, so nothing can be done about it.
    """
    found: List[Position] = []
    for row, col in sorted(free_cells(maze_map)):
        cell = maze_map.cell(row, col)
        if sum(1 for wall in DIRECTIONS if not getattr(cell, wall)) != 1:
            continue
        for direction, (row_delta, col_delta, _) in DIRECTIONS.items():
            neighbour = (row + row_delta, col + col_delta)
            if (
                getattr(cell, direction)
                and maze_map.contains(*neighbour)
                and not maze_map.cell(*neighbour).is_42
            ):
                found.append((row, col))
                break
    return found


def open_areas(maze_map: Map) -> List[Position]:
    """List the top-left corners of the 3x3 squares with no inner wall."""
    found: List[Position] = []
    for top in range(maze_map.rows - 2):
        for left in range(maze_map.cols - 2):
            is_open = True
            for row in range(top, top + 3):
                for col in range(left, left + 3):
                    cell = maze_map.cell(row, col)
                    if col < left + 2 and cell.E:
                        is_open = False
                    if row < top + 2 and cell.S:
                        is_open = False
            if is_open:
                found.append((top, left))
    return found


class TestOpenLoops(unittest.TestCase):
    """Rules of the board: loops, dead-ends, open areas and validity."""

    def test_has_at_least_two_loops(self) -> None:
        for rows, cols, entry, exit in SIZES:
            for seed in SEEDS:
                with self.subTest(rows=rows, cols=cols, seed=seed):
                    board = build_board(rows, cols, entry, exit, seed)
                    self.assertGreaterEqual(count_loops(board), 2)

    def test_dead_ends_are_rare(self) -> None:
        for rows, cols, entry, exit in SIZES:
            for seed in SEEDS:
                with self.subTest(rows=rows, cols=cols, seed=seed):
                    board = build_board(rows, cols, entry, exit, seed)
                    self.assertLessEqual(len(real_dead_ends(board)), 2)

    def test_has_no_open_area(self) -> None:
        for rows, cols, entry, exit in SIZES:
            for seed in SEEDS:
                with self.subTest(rows=rows, cols=cols, seed=seed):
                    board = build_board(rows, cols, entry, exit, seed)
                    self.assertEqual(open_areas(board), [])

    def test_every_free_cell_is_still_reachable(self) -> None:
        # Covers the four corners and the centre, which are free cells.
        for rows, cols, entry, exit in SIZES:
            with self.subTest(rows=rows, cols=cols):
                board = build_board(rows, cols, entry, exit)
                self.assertEqual(reachable(board, entry), free_cells(board))

    def test_centre_is_a_free_cell(self) -> None:
        # The middle column of the "42" drawing is the gap between the
        # two digits, so the centre of the map is never a cell of the "42".
        for rows, cols in ((15, 20), (20, 15), (7, 9), (8, 10), (9, 12)):
            with self.subTest(rows=rows, cols=cols):
                board = build_board(rows, cols, (0, 0), (rows - 1, cols - 1))
                centre = board.cell(rows // 2, (cols - 1) // 2)
                self.assertIs(centre.is_42, False)

    def test_42_and_borders_stay_closed(self) -> None:
        board = build_board(15, 20, (0, 0), (14, 19))
        for row, col in positions(board):
            cell = board.cell(row, col)
            if cell.is_42:
                self.assertEqual(
                    (cell.N, cell.S, cell.E, cell.W), (True,) * 4
                )
        for col in range(20):
            self.assertIs(board.cell(0, col).N, True)
            self.assertIs(board.cell(14, col).S, True)
        for row in range(15):
            self.assertIs(board.cell(row, 0).W, True)
            self.assertIs(board.cell(row, 19).E, True)

    def test_only_opens_walls(self) -> None:
        perfect = wall_snapshot(build_maze(15, 20, (0, 0), (14, 19)))
        board = wall_snapshot(build_board(15, 20, (0, 0), (14, 19)))
        for before, after in zip(perfect, board):
            for was_closed, is_closed in zip(before, after):
                # A wall open in the perfect maze is still open.
                self.assertTrue(was_closed or not is_closed)

    def test_same_seed_gives_same_board(self) -> None:
        first = build_board(15, 20, (0, 0), (14, 19), seed=7)
        second = build_board(15, 20, (0, 0), (14, 19), seed=7)
        self.assertEqual(wall_snapshot(first), wall_snapshot(second))

    def test_path_is_valid_and_not_longer(self) -> None:
        for seed in SEEDS:
            with self.subTest(seed=seed):
                perfect = build_maze(15, 20, (0, 0), (14, 19), seed)
                board = build_board(15, 20, (0, 0), (14, 19), seed)
                letters = shortest_path(board)
                self.assertEqual(walk(board, (0, 0), letters)[-1], (14, 19))
                self.assertLessEqual(
                    len(letters), len(shortest_path(perfect))
                )

    def test_refuses_the_wall_that_completes_an_open_area(self) -> None:
        # 3x3 map: the centre is linked to the four sides, and each corner
        # hangs from one side. The four closed walls are the ones left.
        for seed in SEEDS:
            with self.subTest(seed=seed):
                maze_map = build_map(3, 3, entry=(0, 0), exit=(2, 2))
                for row, col, direction in (
                    (1, 1, "N"), (1, 1, "S"), (1, 1, "E"), (1, 1, "W"),
                    (0, 0, "E"), (0, 2, "S"), (2, 2, "W"), (2, 0, "N"),
                ):
                    maze_map.open_wall(row, col, direction)
                open_loops(maze_map, seed)
                self.assertEqual(open_areas(maze_map), [])
                # Three of the four walls are opened; the last is refused.
                self.assertEqual(count_passages(maze_map), 11)


if __name__ == "__main__":
    unittest.main()
