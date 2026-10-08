"""Terminal rendering: draws a maze map with ASCII characters."""

from typing import List

from src.mazegen.map import Map, Position


# What is drawn inside a cell; every text has the width of one cell.
ENTRY_TEXT = " E "
EXIT_TEXT = " X "
PATTERN_42_TEXT = "###"
PATH_TEXT = " o "
EMPTY_TEXT = "   "
# How a wall is drawn when it is closed and when it is open.
CLOSED_HORIZONTAL = "---"
OPEN_HORIZONTAL = "   "
CLOSED_VERTICAL = "|"
OPEN_VERTICAL = " "
CORNER = "+"
# ANSI code that ends a colour: the text after it uses the terminal default.
RESET_COLOR = "\033[0m"


def paint(text: str, color: str) -> str:
    """Return the text wrapped in a colour code; unchanged without a colour."""
    if not color:
        return text
    return color + text + RESET_COLOR


def cell_text(maze_map: Map, position: Position, show_path: bool) -> str:
    """Return the three characters drawn inside one cell.

    The entry and the exit win over the path, so they stay visible when
    the path is shown.
    """
    cell = maze_map.cell(*position)
    if position == maze_map.entry:
        return ENTRY_TEXT
    if position == maze_map.exit:
        return EXIT_TEXT
    if cell.is_42:
        return PATTERN_42_TEXT
    if show_path and cell.path:
        return PATH_TEXT
    return EMPTY_TEXT


def render_maze(
    maze_map: Map, show_path: bool = False, wall_color: str = ""
) -> str:
    """Draw the map as text, ready to be printed on the terminal.

    Each row of the map becomes two lines: one with the cells and their
    east walls, and one below it with their south walls. The first line of
    the drawing holds the north walls of the first row.

    Args:
        maze_map: map to draw.
        show_path: True to mark the cells whose path flag is set.
        wall_color: ANSI colour code for the walls and corners; an empty
            string draws them without any colour code.

    Returns:
        The lines of the drawing joined by newlines, without a final one.
    """
    # Only what is a wall gets the colour; the inside of a cell never does.
    corner = paint(CORNER, wall_color)
    horizontal = paint(CLOSED_HORIZONTAL, wall_color)
    vertical = paint(CLOSED_VERTICAL, wall_color)
    lines: List[str] = []
    top = corner
    for cell in maze_map.grid[0]:
        top += (horizontal if cell.N else OPEN_HORIZONTAL) + corner
    lines.append(top)
    for row in range(maze_map.rows):
        first = maze_map.cell(row, 0)
        middle = vertical if first.W else OPEN_VERTICAL
        bottom = corner
        for col in range(maze_map.cols):
            cell = maze_map.cell(row, col)
            middle += cell_text(maze_map, (row, col), show_path)
            middle += vertical if cell.E else OPEN_VERTICAL
            bottom += horizontal if cell.S else OPEN_HORIZONTAL
            bottom += corner
        lines.append(middle)
        lines.append(bottom)
    return "\n".join(lines)
