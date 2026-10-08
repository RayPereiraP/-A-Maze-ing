"""Run A-Maze-ing: parse the config, generate, write, draw and show a menu."""

import sys
from typing import Optional, Sequence, Tuple, cast

from src.parser import Config, ConfigError, parse_config
from src.mazegen.maze_generator import MazeGenerator
from src.renderer import render_maze


# Wall colours of the menu, as ANSI codes; the first is the terminal default.
WALL_COLORS: Tuple[str, ...] = (
    "",
    "\033[31m",  # red
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
    "\033[36m",  # cyan
)
# ANSI codes that erase the screen and its history, then move the cursor
# back to the top-left corner.
CLEAR_SCREEN = "\033[2J\033[3J\033[H"
MENU = (
    "=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Quit"
)


def build_generator(config: Config) -> MazeGenerator:
    """Create the generator, and its first maze, from a parsed config.

    Raises:
        ValueError: if the generator refuses the parameters.
    """
    # The config uses (x, y); the map uses (row, col), so they swap.
    entry_x, entry_y = cast(Tuple[int, int], config["ENTRY"])
    exit_x, exit_y = cast(Tuple[int, int], config["EXIT"])
    return MazeGenerator(
        cast(int, config["HEIGHT"]),
        cast(int, config["WIDTH"]),
        entry=(entry_y, entry_x),
        exit=(exit_y, exit_x),
        perfect=cast(bool, config["PERFECT"]),
        # SEED is optional: without it, each run gives a different maze.
        seed=cast(Optional[int], config.get("SEED")),
    )


def clear_screen() -> None:
    """Erase the terminal, so the next drawing starts on an empty screen."""
    # No newline is printed, so the flush is what sends the codes right
    # away, before anything written to stderr.
    print(CLEAR_SCREEN, end="", flush=True)


def regenerate(generator: MazeGenerator, output_file: str) -> None:
    """Build another maze and write it over the output file.

    With a seed, generate() would give the same maze again, so the seed
    moves to the next number first. The mazes of one run are then always
    the same sequence: seed, seed + 1, seed + 2...

    Raises:
        OSError: if the output file cannot be written.
    """
    if generator.seed is not None:
        generator.seed += 1
    generator.generate()
    generator.write(output_file)


def run_menu(generator: MazeGenerator, output_file: str) -> None:
    """Draw the maze and obey the choices of the user until they quit.

    Raises:
        OSError: if a new maze cannot be written to the output file.
        EOFError: if the input ends before the user quits.
    """
    show_path = False
    color_index = 0
    while True:
        print(render_maze(
            generator.maze_map, show_path, WALL_COLORS[color_index]
        ))
        print(MENU)
        choice = input("Choice? (1-4): ").strip()
        while choice not in ("1", "2", "3", "4"):
            print("Invalid choice: type a number from 1 to 4.")
            choice = input("Choice? (1-4): ").strip()
        if choice == "4":
            return
        # Cleared before the action, so a message it prints stays visible.
        clear_screen()
        if choice == "1":
            regenerate(generator, output_file)
        elif choice == "2":
            show_path = not show_path
        else:
            color_index = (color_index + 1) % len(WALL_COLORS)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the whole program for one configuration file.

    Returns:
        0 when the user leaves the menu, 1 after an error message.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config: Config = parse_config(args[0])
        output_file = cast(str, config["OUTPUT_FILE"])
        clear_screen()
        generator = build_generator(config)
        generator.write(output_file)
        run_menu(generator, output_file)
    except ConfigError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: cannot write the output file: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: impossible maze parameters: {error}", file=sys.stderr)
        return 1
    except MemoryError:
        print("Error: the maze is too big for the memory.", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, Ctrl+D or the end of a piped input: leave without a trace.
        print()
        return 0
    return 0
