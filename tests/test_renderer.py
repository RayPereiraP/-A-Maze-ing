"""Tests for Task 8: the terminal rendering."""

import unittest
from typing import List

from src.mazegen import MazeGenerator, shortest_path
from src.mazegen.writer import maze_to_text
from src.renderer import render_maze
from tests.test_maze_generator import build
from tests.test_solver import build_map


def cell_texts(drawing: str) -> List[List[str]]:
    """Read back, from a drawing, the three characters inside each cell."""
    cell_lines = drawing.split("\n")[1::2]
    return [
        [line[start:start + 3] for start in range(1, len(line), 4)]
        for line in cell_lines
    ]


def drawing_to_digits(drawing: str) -> List[str]:
    """Read back the walls of a drawing as the digits of the output file.

    For the cell at (row, col), the north wall is on the line above its
    own, the south wall on the line below, and the west and east walls are
    the characters just before and just after its three characters.
    """
    lines = drawing.split("\n")
    rows = (len(lines) - 1) // 2
    cols = (len(lines[0]) - 1) // 4
    digits: List[str] = []
    for row in range(rows):
        above = lines[2 * row]
        middle = lines[2 * row + 1]
        below = lines[2 * row + 2]
        text = ""
        for col in range(cols):
            start = 4 * col + 1
            value = 0
            if above[start:start + 3] == "---":
                value += 1
            if middle[start + 3] == "|":
                value += 2
            if below[start:start + 3] == "---":
                value += 4
            if middle[start - 1] == "|":
                value += 8
            text += format(value, "X")
        digits.append(text)
    return digits


class TestRenderMaze(unittest.TestCase):
    """Walls, entry, exit, "42" and path of the drawing."""

    def test_small_map_drawn_by_hand(self) -> None:
        # 2x3 map, one corridor: (0,0) E (0,1) E (0,2) S (1,2).
        maze_map = build_map(2, 3, entry=(0, 0), exit=(1, 2))
        maze_map.open_wall(0, 0, "E")
        maze_map.open_wall(0, 1, "E")
        maze_map.open_wall(0, 2, "S")
        shortest_path(maze_map)
        self.assertEqual(
            render_maze(maze_map),
            "+---+---+---+\n"
            "| E         |\n"
            "+---+---+   +\n"
            "|   |   | X |\n"
            "+---+---+---+",
        )
        self.assertEqual(
            render_maze(maze_map, show_path=True),
            "+---+---+---+\n"
            "| E   o   o |\n"
            "+---+---+   +\n"
            "|   |   | X |\n"
            "+---+---+---+",
        )

    def test_drawing_matches_the_output_file(self) -> None:
        for perfect in (True, False):
            for seed in range(5):
                with self.subTest(perfect=perfect, seed=seed):
                    generator = build(perfect=perfect, seed=seed)
                    file_text = maze_to_text(
                        generator.maze_map, generator.path
                    )
                    for show_path in (False, True):
                        drawing = render_maze(generator.maze_map, show_path)
                        self.assertEqual(
                            drawing_to_digits(drawing),
                            file_text.split("\n")[:15],
                        )

    def test_drawing_has_the_size_of_the_map(self) -> None:
        lines = render_maze(build(9, 11, (0, 0), (8, 10)).maze_map)
        self.assertEqual(len(lines.split("\n")), 2 * 9 + 1)
        for line in lines.split("\n"):
            self.assertEqual(len(line), 4 * 11 + 1)

    def test_42_is_visible_in_the_right_cells(self) -> None:
        generator = build()
        texts = cell_texts(render_maze(generator.maze_map, show_path=True))
        for row in range(15):
            for col in range(20):
                is_42 = generator.maze_map.cell(row, col).is_42
                self.assertEqual(texts[row][col] == "###", is_42)
        self.assertEqual(sum(line.count("###") for line in texts), 20)

    def test_entry_and_exit_are_in_their_cells(self) -> None:
        generator = build(9, 11, entry=(8, 0), exit=(0, 10))
        for show_path in (False, True):
            texts = cell_texts(render_maze(generator.maze_map, show_path))
            self.assertEqual(texts[8][0], " E ")
            self.assertEqual(texts[0][10], " X ")
            self.assertEqual(sum(line.count(" E ") for line in texts), 1)
            self.assertEqual(sum(line.count(" X ") for line in texts), 1)

    def test_path_is_hidden_by_default(self) -> None:
        self.assertNotIn("o", render_maze(build().maze_map))

    def test_path_marks_the_cells_between_entry_and_exit(self) -> None:
        generator: MazeGenerator = build()
        texts = cell_texts(render_maze(generator.maze_map, show_path=True))
        for row in range(15):
            for col in range(20):
                position = (row, col)
                on_path = generator.maze_map.cell(row, col).path
                is_end = position in (generator.entry, generator.exit)
                self.assertEqual(
                    texts[row][col] == " o ", on_path and not is_end
                )
        # A path of n letters visits n + 1 cells; two of them are E and X.
        self.assertEqual(
            sum(line.count(" o ") for line in texts), len(generator.path) - 1
        )

    def test_showing_the_path_changes_nothing_else(self) -> None:
        maze_map = build().maze_map
        self.assertEqual(
            render_maze(maze_map, show_path=True).replace("o", " "),
            render_maze(maze_map),
        )

    def test_rendering_does_not_change_the_map(self) -> None:
        generator = build()
        before = maze_to_text(generator.maze_map, generator.path)
        marks = [c.path for row in generator.maze_map.grid for c in row]
        render_maze(generator.maze_map, show_path=True)
        self.assertEqual(
            maze_to_text(generator.maze_map, generator.path), before
        )
        self.assertEqual(
            [c.path for row in generator.maze_map.grid for c in row], marks
        )


if __name__ == "__main__":
    unittest.main()
