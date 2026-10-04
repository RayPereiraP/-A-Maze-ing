#!/usr/bin/env python3

from typing import Optional

from .color_themes import THEMES

# ─── Proportions ──────────────────────────────────────────────────────────
# Each unit = 2 terminal chars wide (one ANSI block).
# CELL_W / CELL_H : size of a cell interior in blocks
# WALL_W / WALL_H : thickness of a wall in blocks

CELL_W = 1   # cell interior width  (blocks)
CELL_H = 1   # cell interior height (lines)
WALL_W = 1   # wall thickness       (blocks)
WALL_H = 1   # wall thickness       (lines)

# according to the size (h*w) of the maze adjust the ratio:

# 9*23 and smaller - 3:1
# 15*31 - 2:1
# bigger - 1:1 (max: 21*45)
# or change it through the menu


# -------------------------------------------------------------------------

def is_pattern(cell: dict[str, bool]) -> bool:
    """A cell is part of the pattern when ALL four walls are closed."""

    return not any(cell.values())


def render_maze(
        cells: list[list[dict[str, bool]]],
        entry: tuple[int, int],
        exit: tuple[int, int],
        theme: str = "default",
        path_coords: Optional[list[tuple[int, int]]] = None) -> str:
    """
    Render the maze.

    Grid structure (WALL_W=1, CELL_W=2, WALL_H=1, CELL_H=2 shown):

        wall_row : [corner][N-wall * CELL_W] ... [corner]
        cell_row : [W-wall][cell    * CELL_W] ... [E-border]   × CELL_H lines
        wall_row : [corner][S-wall  * CELL_W] ... [corner]
        ...

    Each "block" = 2 terminal chars wide (one ANSI colour escape).
    CELL_W, CELL_H, WALL_W, WALL_H control proportions.
    """

    codes = THEMES.get(theme, THEMES["default"])
    height = len(cells)
    width = len(cells[0])

    # path_list is ordered entry→exit; build a set for O(1) cell lookup,
    # and a set of wall gaps the path crosses.

    # Each gap has a canonical ID independent of travel direction:
    #   ("V", x, y)  — vertical gap between column x-1 and x at row y
    #   ("H", x, y)  — horizontal gap between row y-1 and y at column x
    # So wall_v(x,y) checks ("V",x,y) and wall_h(x,y,"S") checks ("H",x,y+1).
    path_list = path_coords or []
    path_set = set(path_list) - {entry, exit}
    path_gaps = set()
    for i in range(len(path_list) - 1):
        cx, cy = path_list[i]
        nx, ny = path_list[i + 1]
        # East:  V-gap right of cx
        if nx == cx + 1:
            path_gaps.add(("V", nx, cy))
        # West:  V-gap right of nx = left of cx
        elif nx == cx - 1:
            path_gaps.add(("V", cx, cy))
        # South: H-gap below cy
        elif ny == cy + 1:
            path_gaps.add(("H", cx, ny))
        # North: H-gap below ny = above cy
        elif ny == cy - 1:
            path_gaps.add(("H", cx, cy))

    def draw_unit(key: str, width: int = 1) -> str:
        """Build a terminal block of `w` units using theme color key."""

        return codes[key] * width

    def cell_code(x: int, y: int) -> str:
        """Return the theme key for cell (x,y)."""

        if (x, y) == entry:
            return "ENTRY"
        if (x, y) == exit:
            return "EXIT"
        if (x, y) in path_set:
            return "PATH"
        if is_pattern(cells[y][x]):
            return "PATTERN"  # inside the pattern
        return "EMPTY"

    def wall_h(x: int, y: int, direction: str, height: int) -> str:
        """
        Horizontal wall segment (N or S) below/above cell (x,y).
        Width = CELL_W blocks.  Returns WALL or the cell colour if open.
        """

        cell = cells[y][x]
        ny = y - 1 if direction == "N" else y + 1
        neighbour = cells[ny][x] if 0 <= ny < height else None

        if not cell[direction]:
            # closed — pattern-to-pattern inner wall gets pattern colour
            if (neighbour is not None
                and is_pattern(cell)
                    and is_pattern(neighbour)):
                return draw_unit("PATTERN", CELL_W)
            return draw_unit("WALL", CELL_W)

        # open — check if the path crosses this gap
        gy = y + 1 if direction == "S" else y   # canonical H-gap row index

        if ("H", x, gy) in path_gaps:
            return draw_unit("PATH", CELL_W)

        return draw_unit("EMPTY", CELL_W)

    def wall_v(x: int, y: int) -> str:
        """
        Vertical wall segment (W side) of cell (x,y).
        Width = WALL_W blocks.  Returns WALL or corridor colour if open.
        """
        if x == 0:
            return draw_unit("WALL", WALL_W)    # outer border always WALL

        cell = cells[y][x]
        left = cells[y][x - 1]

        if not cell["W"]:
            if is_pattern(cell) and is_pattern(left):
                return draw_unit("PATTERN", WALL_W)
            return draw_unit("WALL", WALL_W)

        # open — canonical V-gap is keyed by the right cell's x
        if ("V", x, y) in path_gaps:
            return draw_unit("PATH", WALL_W)

        return draw_unit("EMPTY", WALL_W)

    def corner(x: int, y: int) -> str:
        """
        Corner at the intersection to the bottom-right of cell (x,y).
        PATTERN only if all four surrounding cells are pattern
        (interior corner).
        Otherwise always WALL.
        """

        surrounding = []

        for nx, ny in [(x - 1, y), (x, y), (x - 1, y + 1), (x, y + 1)]:
            if 0 <= nx < width and 0 <= ny < height:
                surrounding.append(cells[ny][nx])

        if surrounding and all(is_pattern(c) for c in surrounding):
            return draw_unit("PATTERN", WALL_W)

        return draw_unit("WALL", WALL_W)

    output = []

    # ── Top border row ───────────────────────────────────────────────────────

    top = ""

    for x in range(width):
        top += draw_unit("WALL", WALL_W)  # corner / left border
        top += wall_h(x, 0, "N", height)

    top += draw_unit("WALL", WALL_W)      # final right corner

    for _ in range(WALL_H):
        output.append(top)

    for y in range(height):

        # ── Cell rows (CELL_H lines each) ────────────────────────────────────

        cell_line = ""

        for x in range(width):
            cell_line += wall_v(x, y)
            cell_line += draw_unit(cell_code(x, y), CELL_W)

        cell_line += draw_unit("WALL", WALL_W)  # right border

        for _ in range(CELL_H):
            output.append(cell_line)

        # ── South wall row ───────────────────────────────────────────────────

        bottom = ""

        for x in range(width):
            bottom += corner(x, y)
            bottom += (draw_unit("WALL", CELL_W)
                       if y == height - 1
                       else wall_h(x, y, "S", height))

        bottom += draw_unit("WALL", WALL_W)

        for _ in range(WALL_H):
            output.append(bottom)

    return "\n".join(output)
