#!/usr/bin/env python3

from typing import Tuple, List, Dict, Any

from pathlib import Path

from .dependencies import (print, BOLD, RESET, YELLOW, BOLD_RED,
                           ValidationError)

from .config import (
    CONFIG, WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, OUTPUT_FILE,
    SEED, THEME, PATTERN
)
from .utils import ConfigError


# ----- PARSERS -----

def parse_coordinates(s: str) -> Tuple[int, int]:
    """Parse 'x,y' string into a tuple of two ints."""
    try:
        x, y = s.split(",")
        return int(x), int(y)

    except ValueError:
        raise ConfigError(f"Invalid coordinates: '{s}' (expected 'x,y')")


def parse_bool(value: str) -> bool:
    """Convert a truthy/falsy string into bool.
    Accepts common variants like yes/no, true/false, 1/0.
    Raises ConfigError for anything ambiguous."""

    val = value.lower()

    if val in ["true", "1", "yes"]:
        return True

    if val in ["false", "0", "no"]:
        return False

    raise ConfigError(f"Invalid boolean: {value}")


def parse_config(config: str) -> Dict[str, Any]:  # Maze:
    """
    Parse the config file and store it into Maze class object.
    """

    # path = Path(config_file_path)
    path = Path(config)

    mandatory_keys = {
        WIDTH,
        HEIGHT,
        ENTRY,
        EXIT,
        PERFECT,
        OUTPUT_FILE
    }

    additional_keys = {
        SEED,
        THEME,
        PATTERN,
        # ALGORITHM
    }

    try:
        lines: List[str] = path.read_text().splitlines()

    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")

    except Exception as e:
        raise ConfigError(e)

    raw_config: Dict[str, Any] = {}

    for line_no, line in enumerate(lines, 1):

        line = line.strip()

        # very strict: does not tolerate trailing whitespaces
        # if line != line.strip():
        #     raise ConfigError(f"Line {line_no} of config file '{path}' "
        #                       "contains whitespace")

        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)

        else:
            print(f"{YELLOW}Warning: Ignoring invalid line {line_no}: "
                  f"'{line}'{RESET}")  # edit text
            continue

        if key not in mandatory_keys and key not in additional_keys:
            print(f"{YELLOW}Warning: Unknown key '{key}' on line {line_no} "
                  f"of config file '{path}' being ignored.{RESET}")
            continue

        if key == ENTRY or key == EXIT:
            raw_config[key] = parse_coordinates(value)
            continue

        if key == PERFECT:
            raw_config[key] = parse_bool(value)
            continue

        if key == THEME:
            raw_config[key] = str(value)

        if key == PATTERN:
            raw_config[key] = str(value)

        raw_config[key] = value

    for key in mandatory_keys:
        if key not in raw_config.keys():
            raise ConfigError(f"Mandatory key {key} missing "
                              f"in the config file {path}")

    return raw_config


# ----- SYS ARGV VALIDATOR -----

def validate_args(argv: List[str]) -> str:
    """Check CLI arguments and return the config file path."""

    argc = len(argv)

    if argc == 1:
        raise ConfigError("No input file provided.\n"
                          f"Correct usage: python3 a_maze_ing.py {CONFIG}")

    if argc > 2:
        raise ConfigError("Too many arguments.\n"
                          f"Correct usage: python3 a_maze_ing.py {CONFIG}")

    if Path(argv[1]).name != CONFIG:
        raise ConfigError("Incorrect input file name.\n"
                          f"Correct usage: python3 a_maze_ing.py {CONFIG}")

    return argv[1]


# ------ DEMO -------

def print_config_info(config: Dict[str, str]) -> None:
    """Display maze config info in readable format."""

    print("✅ Valid maze created:")

    print(f"{BOLD}Width:{RESET}\t\t   {config[WIDTH]}")
    print(f"{BOLD}Height:{RESET}\t\t   {config[HEIGHT]}")
    print(f"{BOLD}Entry coordinates:{RESET} {config[ENTRY]}")
    print(f"{BOLD}Exit coordinates:{RESET}  {config[EXIT]}")
    print(f"{BOLD}Output file:{RESET}\t   {config[OUTPUT_FILE]}")
    print(f"{BOLD}Perfect maze:{RESET}\t   {config[PERFECT]}")

    try:
        print(f"{BOLD}Seed:{RESET}\t\t   {config[SEED]}")
        print(f"{BOLD}Theme:{RESET}\t\t   {config[THEME]}")
        print(f"{BOLD}Pattern:{RESET}\t   {config[PATTERN]}")
    except KeyError:
        pass

    # print(f"{BOLD}Algorithm:{RESET}\t\t{cconfig[ALGORITHM]}")


def main() -> None:
    """Demonstration"""

    print(f"\n{BOLD}Maze config input parsing{RESET}")
    print("-" * 40)

    try:
        import sys
        print_config_info(parse_config(validate_args(sys.argv)))

    except ValidationError as e:
        print(f"\n{BOLD_RED}Error(s) while validating config file:{RESET}\n")
        for err in e.errors():
            print(f"- {err['loc'][0]} → {err['msg']}")

    except ConfigError as e:
        print(f"\n{BOLD_RED}Error:{RESET} {e}")

    finally:
        print()
        print("-" * 40)


if __name__ == "__main__":
    main()
