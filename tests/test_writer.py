"""Tests for Task 5: the output file."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import Optional, Tuple

from src.mazegen import Cell, Map, generate_perfect, shortest_path, write_maze
from src.mazegen.writer import cell_digit, maze_to_text


Position = Tuple[int, int]


def build_map(
    rows: int,
    cols: int,
    entry: Optional[Position] = None,
    exit: Optional[Position] = None,
) -> Map:
    """Build a map with every wall closed, hiding its console messages."""
    with contextlib.redirect_stderr(io.StringIO()):
        return Map(rows, cols, entry, exit)


def written_bytes(maze_map: Map, path: str) -> bytes:
    """Write the map to a temporary file and return its raw bytes."""
    with tempfile.TemporaryDirectory() as folder:
        filename = Path(folder) / "maze.txt"
        write_maze(maze_map, path, filename)
        return filename.read_bytes()


class TestCellDigit(unittest.TestCase):
    """Encoding of the walls of one cell as a hexadecimal digit."""

    def test_all_closed_and_all_open(self) -> None:
        cell = Cell()
        self.assertEqual(cell_digit(cell), "F")
        cell.N = cell.E = cell.S = cell.W = False
        self.assertEqual(cell_digit(cell), "0")

    def test_one_bit_for_each_wall(self) -> None:
        for wall, digit in (("N", "1"), ("E", "2"), ("S", "4"), ("W", "8")):
            with self.subTest(wall=wall):
                cell = Cell()
                cell.N = cell.E = cell.S = cell.W = False
                setattr(cell, wall, True)
                self.assertEqual(cell_digit(cell), digit)

    def test_examples_of_the_subject(self) -> None:
        # "3": open to the south and west. "A": east and west closed.
        cell = Cell()
        cell.S = cell.W = False
        self.assertEqual(cell_digit(cell), "3")
        cell = Cell()
        cell.N = cell.S = False
        self.assertEqual(cell_digit(cell), "A")


class TestOutputFile(unittest.TestCase):
    """Layout and content of the whole file."""

    def test_small_map_written_by_hand(self) -> None:
        # 2x3 map, one corridor: (0,0) E (0,1) E (0,2) S (1,2).
        maze_map = build_map(2, 3, entry=(0, 0), exit=(1, 2))
        maze_map.open_wall(0, 0, "E")
        maze_map.open_wall(0, 1, "E")
        maze_map.open_wall(0, 2, "S")
        self.assertEqual(
            maze_to_text(maze_map, "EES"),
            "D53\n"
            "FFE\n"
            "\n"
            "0,0\n"
            "2,1\n"
            "EES\n",
        )

    def test_entry_and_exit_are_written_as_x_y(self) -> None:
        maze_map = build_map(4, 6, entry=(0, 3), exit=(2, 5))
        lines = maze_to_text(maze_map, "").split("\n")
        self.assertEqual(lines[5], "3,0")
        self.assertEqual(lines[6], "5,2")

    def test_layout_of_a_generated_maze(self) -> None:
        maze_map = build_map(15, 20, (0, 0), (14, 19))
        generate_perfect(maze_map, 42)
        path = shortest_path(maze_map)
        lines = maze_to_text(maze_map, path).split("\n")
        # 15 rows, empty line, entry, exit, path and the final newline.
        self.assertEqual(len(lines), 15 + 1 + 3 + 1)
        for row, line in enumerate(lines[:15]):
            self.assertEqual(len(line), 20)
            for col, digit in enumerate(line):
                self.assertEqual(digit, cell_digit(maze_map.cell(row, col)))
        self.assertEqual(lines[15:], ["", "0,0", "19,14", path, ""])

    def test_file_has_the_same_text_and_unix_newlines(self) -> None:
        maze_map = build_map(7, 9, (0, 0), (6, 8))
        generate_perfect(maze_map, 1)
        path = shortest_path(maze_map)
        data = written_bytes(maze_map, path)
        self.assertEqual(data.decode("utf-8"), maze_to_text(maze_map, path))
        self.assertNotIn(b"\r", data)
        self.assertTrue(data.endswith(b"\n"))

    def test_existing_file_is_replaced(self) -> None:
        maze_map = build_map(2, 2, (0, 0), (1, 1))
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "maze.txt"
            filename.write_text("old content that is much longer\n" * 5)
            write_maze(maze_map, "", filename)
            self.assertEqual(
                filename.read_text(), maze_to_text(maze_map, "")
            )

    def test_missing_entry_or_exit(self) -> None:
        for entry, exit in ((None, (0, 1)), ((0, 0), None)):
            with self.subTest(entry=entry, exit=exit):
                with self.assertRaises(ValueError):
                    maze_to_text(build_map(2, 2, entry, exit), "")


if __name__ == "__main__":
    unittest.main()
