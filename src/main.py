"""Run the first stage of A-Maze-ing: configuration parsing."""

import sys
from pprint import pprint
from typing import Optional, Sequence

from src.parser import Config, ConfigError, parse_config


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Read one configuration argument and display its parsed dictionary."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config: Config = parse_config(args[0])
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    pprint(config, sort_dicts=False)
    return 0
