from .utils import DIRECTIONS
from .maze import Maze


# ------------------ WRITE OUTPUT ----------------------

def _convert_cell_to_hex(cell: dict[str, bool]) -> str:
    """x"""
    num: int = 0
    for d, bit in DIRECTIONS.items():
        if cell[d]:
            num += bit
    return f"{num:X}"


def to_file(maze: Maze, path: str, filename: str) -> None:
    """x"""
    with open(filename, "w", encoding="utf-8") as f:
        for y in maze.grid:
            for x in y:
                f.write(_convert_cell_to_hex(x))
            f.write("\n")
        f.write(f"\n{maze.entry[0]},{maze.entry[1]}"
                f"\n{maze.exit[0]},{maze.exit[1]}"
                f"\n{path}\n")
