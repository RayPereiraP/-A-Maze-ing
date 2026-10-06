"""Maze generation: the perfect maze and the extra loops of a board."""

import random
from typing import List, Optional, Set, Tuple

from src.mazegen.map import DIRECTIONS, Map, Position


# Loops a non-perfect maze must have, so there is always a second route.
MIN_LOOPS: int = 2
# Side, in cells, of the smallest square that counts as a forbidden open area.
OPEN_AREA_SIZE: int = 3


def generate_perfect(maze_map: Map, seed: Optional[int] = None) -> None:
    """Open walls of the map until it is a perfect maze.

    Uses a depth-first search with backtracking: it walks to a random
    unvisited neighbour, opening the wall on the way, and steps back when
    the current cell has no unvisited neighbour left. A wall is only opened
    towards a cell that was never visited, so no loop is ever created.

    The cells of the "42" are never visited, so they stay fully closed. The
    borders stay closed because walls are only opened between two cells.

    Args:
        maze_map: map with every wall still closed; it is changed in place.
        seed: the same seed always gives the same maze; None gives a
            different maze on each call.
    """
    rng = random.Random(seed)
    start: Position = maze_map.entry or (0, 0)
    visited: Set[Position] = {start}
    stack: List[Position] = [start]
    while stack:
        row, col = stack[-1]
        options: List[Tuple[str, Position]] = []
        for direction, (row_delta, col_delta, _) in DIRECTIONS.items():
            neighbour = (row + row_delta, col + col_delta)
            if not maze_map.contains(*neighbour):
                continue
            if maze_map.cell(*neighbour).is_42 or neighbour in visited:
                continue
            options.append((direction, neighbour))
        if not options:
            stack.pop()
            continue
        direction, neighbour = rng.choice(options)
        maze_map.open_wall(row, col, direction)
        visited.add(neighbour)
        stack.append(neighbour)


def open_loops(maze_map: Map, seed: Optional[int] = None) -> None:
    """Open extra walls of a perfect maze so that it gets loops.

    Every closed wall between two normal cells is a candidate, visited in
    random order. A candidate is opened if the maze still has fewer than
    MIN_LOOPS loops, or if one of its two cells is a dead-end. It is never
    opened if that would create an open area of 3x3 cells.

    The maze is already connected, so each wall opened here adds exactly
    one loop. The cells of the "42" and the borders are never touched.

    Args:
        maze_map: map already turned into a perfect maze; changed in place.
        seed: the same seed always opens the same walls.
    """
    rng = random.Random(seed)
    candidates: List[Tuple[Position, str, Position]] = []
    for row in range(maze_map.rows):
        for col in range(maze_map.cols):
            for direction in ("S", "E"):
                row_delta, col_delta, _ = DIRECTIONS[direction]
                neighbour = (row + row_delta, col + col_delta)
                if not maze_map.contains(*neighbour):
                    continue
                if maze_map.cell(row, col).is_42:
                    continue
                if maze_map.cell(*neighbour).is_42:
                    continue
                if getattr(maze_map.cell(row, col), direction):
                    candidates.append(((row, col), direction, neighbour))
    rng.shuffle(candidates)

    loops = 0
    for origin, direction, neighbour in candidates:
        wanted = (
            loops < MIN_LOOPS
            or _is_dead_end(maze_map, origin)
            or _is_dead_end(maze_map, neighbour)
        )
        if wanted and not _completes_open_area(maze_map, origin, neighbour):
            maze_map.open_wall(*origin, direction)
            loops += 1


def _is_dead_end(maze_map: Map, position: Position) -> bool:
    """Tell whether the cell has exactly one open wall."""
    cell = maze_map.cell(*position)
    return sum(1 for wall in DIRECTIONS if not getattr(cell, wall)) == 1


def _completes_open_area(
    maze_map: Map, first: Position, second: Position
) -> bool:
    """Tell whether opening the wall between two cells makes an open area.

    An open area is a square of OPEN_AREA_SIZE cells a side with every
    inner wall open. The wall between the two cells is still closed, so a
    square that holds both cells and misses only one inner wall would
    become an open area.
    """
    inner_walls = 2 * OPEN_AREA_SIZE * (OPEN_AREA_SIZE - 1)
    last = OPEN_AREA_SIZE - 1
    low_row, high_row = sorted((first[0], second[0]))
    low_col, high_col = sorted((first[1], second[1]))
    # Every square that holds both cells, given by its top-left corner.
    for top in range(high_row - last, low_row + 1):
        for left in range(high_col - last, low_col + 1):
            if not maze_map.contains(top, left):
                continue
            if not maze_map.contains(top + last, left + last):
                continue
            if _open_inner_walls(maze_map, top, left) == inner_walls - 1:
                return True
    return False


def _open_inner_walls(maze_map: Map, top: int, left: int) -> int:
    """Count the open walls between the cells of one square of the map."""
    last = OPEN_AREA_SIZE - 1
    count = 0
    for row in range(top, top + OPEN_AREA_SIZE):
        for col in range(left, left + OPEN_AREA_SIZE):
            cell = maze_map.cell(row, col)
            if col < left + last and not cell.E:
                count += 1
            if row < top + last and not cell.S:
                count += 1
    return count
