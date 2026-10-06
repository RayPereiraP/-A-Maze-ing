"""Run the first stage of A-Maze-ing: configuration parsing."""

import sys
from typing import Optional, Sequence, Tuple, cast

from src.parser import Config, ConfigError, parse_config
from src.mazegen.maze_generator import MazeGenerator
from src.renderer import render_maze


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
        generator = MazeGenerator(
            cast(int, config["HEIGHT"]),
            cast(int, config["WIDTH"]),
            entry=(entry_y, entry_x),
            exit=(exit_y, exit_x),
            perfect=cast(bool, config["PERFECT"]),
            # SEED is optional: without it, each run gives a different maze.
            seed=cast(Optional[int], config.get("SEED")),
        )
        generator.write(cast(str, config["OUTPUT_FILE"]))
        print(render_maze(generator.maze_map, show_path=True))
        print(generator.path)
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: cannot write the output file: {error}", file=sys.stderr)
        return 1
    return 0
