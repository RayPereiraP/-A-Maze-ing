"""Maze output: writes the map in the file format of the subject."""

from pathlib import Path
from typing import Dict, List, Union

from src.mazegen.cell import Cell
from src.mazegen.map import Map


# wall -> value of its bit in the hexadecimal digit of a cell
WALL_BITS: Dict[str, int] = {"N": 1, "E": 2, "S": 4, "W": 8}


def cell_digit(cell: Cell) -> str:
    """Return the hexadecimal digit that encodes the closed walls of a cell.

    Each closed wall adds the value of its bit, so a cell with every wall
    closed is "F" (1 + 2 + 4 + 8) and one with every wall open is "0".
    """
    value = 0
    for wall, bit in WALL_BITS.items():
        if getattr(cell, wall):
            value += bit
    return format(value, "X")


def maze_to_text(maze_map: Map, path: str) -> str:
    """Build the whole content of the output file.

    The content is one line of digits for each row of the map, an empty
    line, the entry, the exit and the path. Every line ends with a newline.
    The entry and the exit are written as "x,y", that is, column first.

    Args:
        maze_map: map with an entry, an exit and its walls already opened.
        path: letters of the shortest path from the entry to the exit.

    Raises:
        ValueError: if the map has no entry or no exit.
    """
    if maze_map.entry is None or maze_map.exit is None:
        raise ValueError("The map needs an entry and an exit.")
    entry_row, entry_col = maze_map.entry
    exit_row, exit_col = maze_map.exit
    lines: List[str] = [
        "".join(cell_digit(cell) for cell in row) for row in maze_map.grid
    ]
    lines.append("")
    lines.append(f"{entry_col},{entry_row}")
    lines.append(f"{exit_col},{exit_row}")
    lines.append(path)
    return "".join(line + "\n" for line in lines)


def write_maze(maze_map: Map, path: str, filename: Union[str, Path]) -> None:
    """Write the map, its entry, its exit and the path to a file.

    Args:
        maze_map: map with an entry, an exit and its walls already opened.
        path: letters of the shortest path from the entry to the exit.
        filename: file to create; an existing file is replaced.

    Raises:
        ValueError: if the map has no entry or no exit.
        OSError: if the file cannot be written.
    """
    text = maze_to_text(maze_map, path)
    # newline="\n" stops Windows from turning each "\n" into "\r\n".
    with open(filename, "w", encoding="utf-8", newline="\n") as file:
        file.write(text)
