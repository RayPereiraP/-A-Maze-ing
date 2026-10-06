"""Tests for Task 7: the MazeGenerator class."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional, Tuple

from src.mazegen import Map, MazeGenerator
from src.mazegen.writer import maze_to_text
from tests.test_generator import (
    count_passages,
    free_cells,
    reachable,
    wall_snapshot,
)
from tests.test_solver import walk


Position = Tuple[int, int]
# The scripts run from here so that "import src.mazegen" works.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build(
    rows: int = 15,
    cols: int = 20,
    entry: Position = (0, 0),
    exit: Position = (14, 19),
    perfect: bool = False,
    seed: Optional[int] = 42,
) -> MazeGenerator:
    """Create a generator, hiding the console messages of the map."""
    with contextlib.redirect_stderr(io.StringIO()):
        return MazeGenerator(rows, cols, entry, exit, perfect, seed)


def count_loops(maze_map: Map) -> int:
    """Count the independent loops: passages - cells + 1."""
    return count_passages(maze_map) - len(free_cells(maze_map)) + 1


class TestMazeGenerator(unittest.TestCase):
    """Parameters, generation, access to the result and errors."""

    def test_five_line_script(self) -> None:
        # The "done when" of the task: import, generate, read the path.
        script = (
            "from src.mazegen import MazeGenerator\n"
            "generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19),"
            " seed=42)\n"
            "print(generator.path)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT,
        )
        self.assertEqual(result.stdout.strip(), build().path)

    def test_stores_the_parameters(self) -> None:
        generator = build(9, 11, (8, 0), (0, 10), perfect=True, seed=3)
        self.assertEqual((generator.rows, generator.cols), (9, 11))
        self.assertEqual(generator.entry, (8, 0))
        self.assertEqual(generator.exit, (0, 10))
        self.assertIs(generator.perfect, True)
        self.assertEqual(generator.seed, 3)

    def test_gives_access_to_the_structure(self) -> None:
        generator = build()
        maze_map = generator.maze_map
        self.assertIsInstance(maze_map, Map)
        self.assertEqual((maze_map.rows, maze_map.cols), (15, 20))
        self.assertEqual(maze_map.entry, (0, 0))
        self.assertEqual(maze_map.exit, (14, 19))
        self.assertEqual(reachable(maze_map, (0, 0)), free_cells(maze_map))

    def test_path_leads_from_entry_to_exit(self) -> None:
        for perfect in (True, False):
            with self.subTest(perfect=perfect):
                generator = build(perfect=perfect)
                visited = walk(generator.maze_map, (0, 0), generator.path)
                self.assertEqual(visited[-1], (14, 19))

    def test_perfect_mode_has_no_loops(self) -> None:
        self.assertEqual(count_loops(build(perfect=True).maze_map), 0)

    def test_default_mode_has_loops(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            generator = MazeGenerator(15, 20, (0, 0), (14, 19))
        self.assertIs(generator.perfect, False)
        self.assertGreaterEqual(count_loops(generator.maze_map), 2)

    def test_same_seed_gives_same_maze(self) -> None:
        first, second = build(seed=7), build(seed=7)
        self.assertEqual(
            wall_snapshot(first.maze_map), wall_snapshot(second.maze_map)
        )
        self.assertEqual(first.path, second.path)

    def test_generate_builds_a_new_maze(self) -> None:
        generator = build(seed=1)
        old_map = generator.maze_map
        old_walls = wall_snapshot(old_map)
        generator.generate()
        self.assertIsNot(generator.maze_map, old_map)
        self.assertEqual(wall_snapshot(generator.maze_map), old_walls)
        generator.seed = 2
        generator.generate()
        self.assertNotEqual(wall_snapshot(generator.maze_map), old_walls)
        visited = walk(generator.maze_map, (0, 0), generator.path)
        self.assertEqual(visited[-1], (14, 19))

    def test_write_creates_the_output_file(self) -> None:
        generator = build()
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "maze.txt"
            generator.write(filename)
            self.assertEqual(
                filename.read_bytes().decode("utf-8"),
                maze_to_text(generator.maze_map, generator.path),
            )

    def test_invalid_parameters(self) -> None:
        cases = (
            (0, 5, (0, 0), (0, 1)),
            (5, 0, (0, 0), (1, 0)),
            (5, 5, (5, 0), (0, 0)),
            (5, 5, (0, -1), (0, 0)),
            (5, 5, (0, 0), (0, 5)),
            (5, 5, (2, 2), (2, 2)),
        )
        for rows, cols, entry, exit in cases:
            with self.subTest(rows=rows, cols=cols, entry=entry, exit=exit):
                with self.assertRaises(ValueError):
                    build(rows, cols, entry, exit)

    def test_does_not_load_the_parser(self) -> None:
        script = (
            "import sys\n"
            "import src.mazegen\n"
            "print('src.parser' in sys.modules, 'src.main' in sys.modules)\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT,
        )
        self.assertEqual(result.stdout.strip(), "False False")


if __name__ == "__main__":
    unittest.main()
