"""Run the first stage of A-Maze-ing: configuration parsing."""

import sys
from pprint import pprint
from typing import Optional, Sequence, Tuple, cast

from src.parser import Config, ConfigError, parse_config
from src.mazegen.map import Map


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Read one configuration argument and display its parsed dictionary."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config: Config = parse_config(args[0])
        # The config uses (x, y); the map uses (row, col), so they swap.
        entry_x, entry_y = cast(Tuple[int, int], config["ENTRY"])
        exit_x, exit_y = cast(Tuple[int, int], config["EXIT"])
        project_map = Map(
            cast(int, config["HEIGHT"]),
            cast(int, config["WIDTH"]),
            entry=(entry_y, entry_x),
            exit=(exit_y, exit_x),
        )
        for row in project_map.grid:
            for cell in row:
                pprint(vars(cell), sort_dicts=False)
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    # pprint(config, sort_dicts=False)
    return 0
