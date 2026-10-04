# import sys
from random import seed
from typing import Optional, Tuple, Dict, List, Any
from pathlib import Path

from .algorithm import Algorithm
from .utils import (
    Maze, BaseModel, Field, model_validator, PrivateAttr,
    print, BOLD_RED, RESET, PATTERNS,
    WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, OUTPUT_FILE,
    PATTERN, SEED, THEME,
    parse_config, validate_args,
    load_output_file, read_coordinates,
    read_maze_lines, parse_maze, read_path,
    to_file, render_maze
)


class MazeGenerator(BaseModel):
    # --- Validation of config input - mandatory fields ---
    width: int = Field(..., ge=2, le=45)  # max: backtracker recursion limit
    height: int = Field(..., ge=2, le=45)  # max: backtracker recursion limit
    entry: Tuple[int, int] = Field(...)
    exit: Tuple[int, int] = Field(...)
    output_file: str = Field(...)
    perfect: bool = Field(...)

    # --- Optional fields ---
    seed: Optional[int] = Field(default=None, ge=0)
    theme: str = "default"
    pattern: str = "42"
    # algorithm:

    # --- Internal attributes ---
    _maze: "Maze" = PrivateAttr()
    _algorithm: "Algorithm" = PrivateAttr()

    @model_validator(mode="after")
    def validate_and_build_maze(self) -> "MazeGenerator":
        """Validate coordinates + allocate the maze structure."""

        errors = []

        # ---- ENTRY ----
        if len(self.entry) != 2:
            errors.append("ENTRY must contain exactly two integers (x,y).")

        entry_x, entry_y = self.entry
        if entry_x < 0 or entry_y < 0:
            errors.append("ENTRY coordinates must be non-negative.")

        if entry_x >= self.width or entry_y >= self.height:
            errors.append("ENTRY is outside maze bounds.")

        # ---- EXIT ----
        if len(self.exit) != 2:
            errors.append("EXIT must contain exactly two integers (x,y).")

        exit_x, exit_y = self.exit
        if exit_x < 0 or exit_y < 0:
            errors.append("EXIT coordinates must be non-negative.")

        if exit_x >= self.width or exit_y >= self.height:
            errors.append("EXIT is outside maze bounds.")

        # ENTRY != EXIT
        if self.entry == self.exit:
            errors.append("ENTRY and EXIT cannot match.")

        # PATTERN_SIZE vs MAZE size
        # if self.pattern:
        #     pattern_width = len(self.pattern[0])
        #     pattern_height = len(self.pattern)

            # if pattern_width > self.width - 2:
            #     errors.append(f"Pattern width ({pattern_width}) is too "
            #                   f"large for maze width ({self.width}). "
            #                   "Decrease pattern width or increase "
            #                   "the maze width.")
            # if pattern_height > self.height - 2:
            #     errors.append(f"Pattern height ({pattern_height}) is too "
            #                   f"large for maze height ({self.height}). "
            #                   "Decrease pattern height or increase "
            #                   "the maze height")

        # Output file format check
        if not self.output_file.endswith(".txt"):
            errors.append("OUTPUT_FILE must have a .txt extension.")

        if errors:
            raise ValueError("\n".join(errors))

        return self

    # ------- Utility methods - generator ---------

    @classmethod
    def from_cli(cls, args: list[str]) -> "MazeGenerator":
        """Use this method to instantiate class object with sys argv."""

        maze_config = parse_config(validate_args(args))

        data = {
            "width": maze_config[WIDTH],
            "height": maze_config[HEIGHT],
            "entry": maze_config[ENTRY],
            "exit": maze_config[EXIT],
            "perfect": maze_config[PERFECT],
            "output_file": maze_config[OUTPUT_FILE]
        }

        pattern = maze_config.get(PATTERN)
        theme = maze_config.get(THEME)
        seed = maze_config.get(SEED)

        if pattern is not None:
            data["pattern"] = pattern

        if theme is not None:
            data["theme"] = theme

        if seed is not None:
            data["seed"] = seed

        # algorithm=maze_config[ALGORITHM]

        return cls(**data)

    def _fill_pattern(self, pattern: str) -> None:
        """Write the chosen pattern to the maze base"""

        if not pattern:
            return

        if pattern not in PATTERNS:
            print(
                f"\n{BOLD_RED}ALERT:{RESET} Invalid pattern '{pattern}'.\n"
                f"Available patterns: {', '.join(PATTERNS)}\n"
            )
            return

        pattern_data = PATTERNS[pattern]["pattern"]
        if pattern_data is None:
            return

        pattern_width = PATTERNS[pattern]["width"]
        pattern_height = PATTERNS[pattern]["height"]

        if (self.width < pattern_width + 2
                or self.height < pattern_height + 2):
            print(f"\n{BOLD_RED}ALERT:{RESET} Chosen pattern doesn't fit in "
                  f"the maze. Maze at least {pattern_width + 2} wide and "
                  f"{pattern_height + 2} high is needed.\n")
            return

        # centered
        start_x = self.width // 2 - pattern_width // 2
        start_y = self.height // 2 - pattern_height // 2

        # verify ENTRY/EXIT vs PATTERN
        for y in range(pattern_height):
            for x in range(pattern_width):
                if pattern_data[y][x] != "0":  # == 1
                    if ((start_x + x, start_y + y) == self.entry
                            or (start_x + x, start_y + y) == self.exit):
                        print(f"{BOLD_RED}ALERT:{RESET} Entry or exit are "
                              "inside the chosen pattern. "
                              "Pattern is being ignored.")
                        return

        for y in range(pattern_height):
            for x in range(pattern_width):
                if pattern_data[y][x] != "0":  # == 1
                    try:
                        (self._maze.get_cell(start_x + x,
                                             start_y + y))["pattern"] = True
                    except TypeError:
                        continue

    def generate(self) -> None:
        """Regenerate new maze"""

        self._maze = Maze(self.width, self.height, self.entry, self.exit)

        if self.pattern:
            self._fill_pattern(self.pattern)

        seed(self.seed)

        self._algorithm = Algorithm(self._maze, self.perfect)
        self._algorithm.backtracker(*self.entry)  # hardcoded backtracker

        # write the generated maze to output file
        to_file(self._maze, self._algorithm.get_path(), self.output_file)

    def _read_output(self) -> Dict[str, Any]:
        """Show the generated maze from output file in terminal"""

        lines = load_output_file(Path(self.output_file))
        entry, exit = read_coordinates(lines)
        cells = parse_maze(read_maze_lines(lines))
        path = read_path(entry, lines)

        return {
            "lines": lines,
            "entry": entry,
            "exit": exit,
            "cells": cells,
            "path": path
        }

    def get_path_coords(self) -> List[Tuple[int, int]]:
        """Return the path as a list of (x, y) coordinates."""
        maze_info = self._read_output()
        return list(maze_info["path"])

    def render_maze_visual(
            self, show_path: bool = False,
            path_coords: Optional[List[Tuple[int, int]]] = None) -> str:
        """Render the generated maze as a Rich markup string."""
        maze_info = self._read_output()
        entry = maze_info["entry"]
        exit = maze_info["exit"]
        cells = maze_info["cells"]

        path = None
        if path_coords is not None:
            path = path_coords
        elif show_path:
            path = list(maze_info["path"])

        return str(render_maze(cells, entry, exit, self.theme, path))
