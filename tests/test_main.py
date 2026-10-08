"""Tests for Task 9: the interactive menu and the whole program."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union
from unittest.mock import patch

from src.main import CLEAR_SCREEN, MENU, WALL_COLORS, main
from src.mazegen import MazeGenerator
from src.mazegen.writer import maze_to_text
from src.renderer import RESET_COLOR, render_maze
from tests.test_maze_generator import build


Answer = Union[str, BaseException]
CONFIG = (
    "# default test config\n"
    "WIDTH=20\n"
    "HEIGHT=15\n"
    "ENTRY=0,0\n"
    "EXIT=19,14\n"
    "OUTPUT_FILE={output}\n"
    "PERFECT={perfect}\n"
    "{extra}"
)


class ProgramTestCase(unittest.TestCase):
    """Run main() in a temporary folder, typing the answers of the menu."""

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.output = self.folder / "maze.txt"

    def write_config(
        self, perfect: bool = True, extra: str = "SEED=7\n"
    ) -> str:
        """Write a config file and return its name."""
        config = self.folder / "config.txt"
        config.write_text(
            CONFIG.format(output=self.output, perfect=perfect, extra=extra),
            encoding="utf-8",
        )
        return str(config)

    def run_program(
        self, args: List[str], answers: Sequence[Answer]
    ) -> Tuple[int, str, str]:
        """Run main() and return its code and what it printed.

        Each answer is what one call to input() gives: a typed line, or an
        exception such as KeyboardInterrupt. Running out of answers makes
        the test fail, so a menu that never quits is noticed.
        """
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("builtins.input", side_effect=answers):
            with contextlib.redirect_stdout(stdout):
                with contextlib.redirect_stderr(stderr):
                    code = main(args)
        # The codes that clear the screen are taken out of the returned
        # stdout; the untouched text stays in self.raw_stdout.
        self.raw_stdout = stdout.getvalue()
        return (
            code,
            self.raw_stdout.replace(CLEAR_SCREEN, ""),
            stderr.getvalue(),
        )

    def expected(self, seed: Optional[int] = 7) -> MazeGenerator:
        """Build, without the program, the maze a seed must give."""
        return build(perfect=True, seed=seed)


class TestMenu(ProgramTestCase):
    """The interactions asked by the subject."""

    def test_runs_from_start_to_end(self) -> None:
        code, out, err = self.run_program([self.write_config()], ["4"])
        generator = self.expected()
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(
            out, render_maze(generator.maze_map) + "\n" + MENU + "\n"
        )
        self.assertEqual(
            self.output.read_text(encoding="utf-8"),
            maze_to_text(generator.maze_map, generator.path),
        )

    def test_regenerate_draws_and_writes_another_maze(self) -> None:
        code, out, _ = self.run_program([self.write_config()], ["1", "4"])
        first, second = self.expected(7), self.expected(8)
        self.assertEqual(code, 0)
        self.assertNotEqual(
            render_maze(first.maze_map), render_maze(second.maze_map)
        )
        self.assertEqual(
            out,
            render_maze(first.maze_map) + "\n" + MENU + "\n"
            + render_maze(second.maze_map) + "\n" + MENU + "\n",
        )
        self.assertEqual(
            self.output.read_text(encoding="utf-8"),
            maze_to_text(second.maze_map, second.path),
        )

    def test_regenerate_without_seed_gives_a_valid_maze(self) -> None:
        config = self.write_config(extra="")
        code, out, _ = self.run_program([config], ["1", "1", "4"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count(MENU), 3)
        lines = self.output.read_text(encoding="utf-8").split("\n")
        self.assertEqual(len(lines[0]), 20)
        self.assertEqual(lines[15:18], ["", "0,0", "19,14"])

    def test_path_is_hidden_then_shown_then_hidden(self) -> None:
        answers: List[Answer] = ["2", "2", "4"]
        _, out, _ = self.run_program([self.write_config()], answers)
        maze_map = self.expected().maze_map
        hidden = render_maze(maze_map) + "\n" + MENU + "\n"
        shown = render_maze(maze_map, show_path=True) + "\n" + MENU + "\n"
        self.assertNotEqual(hidden, shown)
        self.assertEqual(out, hidden + shown + hidden)

    def test_path_stays_shown_after_regenerating(self) -> None:
        answers: List[Answer] = ["2", "1", "4"]
        _, out, _ = self.run_program([self.write_config()], answers)
        second = render_maze(self.expected(8).maze_map, show_path=True)
        self.assertTrue(out.endswith(second + "\n" + MENU + "\n"))

    def test_wall_colours_rotate_and_come_back(self) -> None:
        answers = ["3"] * len(WALL_COLORS) + ["4"]
        _, out, _ = self.run_program([self.write_config()], answers)
        maze_map = self.expected().maze_map
        drawings = [render_maze(maze_map, False, c) for c in WALL_COLORS]
        self.assertEqual(len(set(drawings)), len(WALL_COLORS))
        self.assertEqual(
            out,
            "".join(d + "\n" + MENU + "\n" for d in drawings + drawings[:1]),
        )

    def test_screen_is_cleared_before_each_drawing(self) -> None:
        self.run_program([self.write_config()], ["1", "2", "3", "4"])
        # One screen at the start and one per action; quitting draws none.
        screens = self.raw_stdout.split(CLEAR_SCREEN)
        self.assertEqual(screens[0], "")
        self.assertEqual(len(screens[1:]), 4)
        for screen in screens[1:]:
            self.assertEqual(screen.count(" E "), 1)
            self.assertTrue(screen.endswith(MENU + "\n"))

    def test_invalid_choice_does_not_clear_the_screen(self) -> None:
        self.run_program([self.write_config()], ["9", "x", "4"])
        self.assertEqual(self.raw_stdout.count(CLEAR_SCREEN), 1)

    def test_invalid_choices_are_asked_again(self) -> None:
        answers: List[Answer] = ["", "0", "5", "abc", " 2 ", "4"]
        code, out, err = self.run_program([self.write_config()], answers)
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out.count("Invalid choice"), 4)
        # The maze is drawn twice only: at the start and after the "2".
        self.assertEqual(out.count(MENU), 2)


class TestWallColour(unittest.TestCase):
    """The colour reaches the walls and nothing else."""

    def test_removing_the_codes_gives_the_plain_drawing(self) -> None:
        maze_map = build().maze_map
        for color in WALL_COLORS[1:]:
            drawing = render_maze(maze_map, True, color)
            self.assertIn(color, drawing)
            self.assertEqual(
                drawing.replace(color, "").replace(RESET_COLOR, ""),
                render_maze(maze_map, True),
            )

    def test_only_walls_are_coloured(self) -> None:
        color = WALL_COLORS[1]
        drawing = render_maze(build().maze_map, True, color)
        for piece in drawing.split(color)[1:]:
            self.assertIn(piece.split(RESET_COLOR)[0], ("+", "---", "|"))


class TestErrors(ProgramTestCase):
    """No error brings the program down."""

    def assert_error(self, args: List[str], message: str) -> None:
        """Check that main() ends with code 1 and one clear message."""
        code, out, err = self.run_program(args, [])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(message, err)
        self.assertNotIn("Traceback", err)

    def test_wrong_number_of_arguments(self) -> None:
        self.assert_error([], "Usage:")
        self.assert_error(["a.txt", "b.txt"], "Usage:")

    def test_missing_config_file(self) -> None:
        self.assert_error([str(self.folder / "nothing.txt")], "Cannot read")

    def test_bad_syntax(self) -> None:
        config = self.write_config(extra="this line has no equal sign\n")
        self.assert_error([config], "expected KEY=VALUE")

    def test_impossible_parameters(self) -> None:
        for old, new, message in (
            ("WIDTH=20", "WIDTH=0", "WIDTH must be greater than zero"),
            ("EXIT=19,14", "EXIT=20,14", "EXIT must be inside the maze"),
            ("EXIT=19,14", "EXIT=0,0", "must be different cells"),
        ):
            config = self.folder / "config.txt"
            text = CONFIG.format(output=self.output, perfect=True, extra="")
            config.write_text(text.replace(old, new), encoding="utf-8")
            with self.subTest(message=message):
                self.assert_error([str(config)], message)

    def test_output_file_cannot_be_written(self) -> None:
        self.output = self.folder / "missing_folder" / "maze.txt"
        self.assert_error([self.write_config()], "cannot write the output")

    def test_generator_refusing_the_parameters(self) -> None:
        with patch(
            "src.main.MazeGenerator", side_effect=ValueError("too odd")
        ):
            self.assert_error([self.write_config()], "impossible maze")

    def test_ctrl_c_and_end_of_input_leave_quietly(self) -> None:
        for answer in (KeyboardInterrupt(), EOFError()):
            with self.subTest(answer=type(answer).__name__):
                code, _, err = self.run_program(
                    [self.write_config()], ["2", answer]
                )
                self.assertEqual(code, 0)
                self.assertEqual(err, "")

    def test_small_maze_omits_the_42_and_still_runs(self) -> None:
        config = self.folder / "config.txt"
        config.write_text(
            f"WIDTH=3\nHEIGHT=2\nENTRY=0,0\nEXIT=2,1\n"
            f"OUTPUT_FILE={self.output}\nPERFECT=False\n",
            encoding="utf-8",
        )
        code, out, err = self.run_program([str(config)], ["1", "2", "3", "4"])
        self.assertEqual(code, 0)
        self.assertIn("pattern omitted", err)
        self.assertEqual(out.count(MENU), 4)


if __name__ == "__main__":
    unittest.main()
