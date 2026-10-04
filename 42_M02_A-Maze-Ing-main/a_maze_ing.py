#!/usr/bin/env python3

import sys

from mazegen import (
    ConfigError, MazeGenError, ValidationError,
    MazeGenerator,
    print, Text, Panel,
    RESET, BOLD_RED,
    THEMES, PATTERNS
)

MENU_TEXT = (
    "1) Re-generate    2) Show/Hide path\n"
    "3) Change theme   4) Change pattern\n"
    "5) Quit"
)


def print_screen(maze: str) -> None:
    print(Text.from_markup(maze))
    print(Panel(Text.from_markup(MENU_TEXT), expand=False))


def main() -> None:
    """Entry point of the A-Maze-Ing program"""

    try:
        generator = MazeGenerator.from_cli(sys.argv)
        generator.generate()

        show_path = False
        maze = generator.render_maze_visual(show_path)

        themes = list(THEMES.keys())
        patterns = list(PATTERNS.keys())
        theme_index = (themes.index(generator.theme)
                       if generator.theme in themes
                       else 0)
        pattern_index = (patterns.index(generator.pattern)
                         if generator.pattern in patterns
                         else 0)

        print_screen(maze)

        while True:

            choice = input("Your choice (1-5): ").strip()

            if choice == "1":
                generator.generate()
                maze = generator.render_maze_visual(show_path)
                print_screen(maze)

            elif choice == "2":
                show_path = not show_path
                maze = generator.render_maze_visual(show_path)
                print_screen(maze)

            elif choice == "3":
                theme_index = (theme_index + 1) % len(themes)
                generator.theme = themes[theme_index]
                maze = generator.render_maze_visual(show_path)
                print_screen(maze)

            elif choice == "4":
                pattern_index = (pattern_index + 1) % len(patterns)
                generator.pattern = patterns[pattern_index]
                generator.generate()
                maze = generator.render_maze_visual(show_path)
                print_screen(maze)

            elif choice == "5":
                break

            else:
                print(f"{BOLD_RED}Alert:{RESET} Choose from options 1-5.\n")

    except ValidationError as e:
        print(f"{BOLD_RED}Error(s) while validating config file:{RESET}")
        for err in e.errors():
            location = ".".join(map(str, err['loc'])) if err['loc'] \
                else "model"
            messages = err["msg"].split("\n")
            for msg in messages:
                msg = msg.removeprefix("Value error, ")
                print(f"- {location} → {msg}")

    except (ConfigError, MazeGenError) as e:
        print(f"{BOLD_RED}Error:{RESET} {e}")


if __name__ == "__main__":
    main()
