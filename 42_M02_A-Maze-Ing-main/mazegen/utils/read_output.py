from .utils import DIRECTIONS, DIR_VECTORS, MazeGenError

from pathlib import Path
from typing import List, Tuple


# ------------------ READ OUTPUT ----------------------

def _convert_hex_to_cell(hex_digit: str) -> dict[str, bool]:
    """Convert one hex digit into a dict of open/closed directions."""
    num = int(hex_digit, 16)

    # True = open, False = closed wall
    return {d: not bool(num & bit) for d, bit in DIRECTIONS.items()}


def load_output_file(path: Path) -> List[str]:
    """Read a maze generator output text file into str."""

    try:
        with path.open(mode="r", encoding="utf-8") as file:
            return file.read().splitlines()

    except Exception as e:
        raise MazeGenError(f"The output file {path} cannot be read: {e}.")


def read_maze_lines(lines: List[str]) -> List[List[str]]:
    """Returns only maze lines from the output file."""

    empty_line_index = lines.index("")

    maze_lines = lines[:empty_line_index]

    return [list(row) for row in maze_lines]


def read_coordinates(
        lines: List[str]
        ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Returns transformed coordinates of entry and exit point
    from the output file."""

    empty_line_index = lines.index("")

    entry_line = lines[empty_line_index + 1]
    exit_line = lines[empty_line_index + 2]

    entry_x, entry_y = entry_line.split(",")
    entry: Tuple[int, int] = (int(entry_x), int(entry_y))

    exit_x, exit_y = exit_line.split(",")
    exit: Tuple[int, int] = (int(exit_x), int(exit_y))

    return (entry, exit)


def read_path(
        entry: Tuple[int, int],
        lines: List[str]
        ) -> list[Tuple[int, int]]:
    """Returns the path line from the output file."""

    empty_line_index = lines.index("")

    x, y = entry
    coords = [(x, y)]
    for char in lines[empty_line_index + 3]:
        dir_x, dir_y = DIR_VECTORS[char]
        x += dir_x
        y += dir_y
        coords.append((x, y))
    return coords

    # return lines[empty_line_index + 3]


# def path_to_coords(entry, path_string):
#     x, y = entry
#     coords = [(x, y)]
#     for char in path_string:
#         dir_x, dir_y = DIR_VECTORS[char]
#         x += dir_x
#         y += dir_y
#         coords.append((x, y))
#     return set(coords)


def parse_maze(maze_lines: List[List[str]]) -> List[List[dict[str, bool]]]:
    return [[_convert_hex_to_cell(c) for c in row] for row in maze_lines]
