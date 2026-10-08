"""Maze solving: shortest path from the entry to the exit."""

from collections import deque
from typing import Deque, Dict, List, Tuple

from .map import DIRECTIONS, Map, Position


def shortest_path(maze_map: Map) -> str:
    """Find the shortest path from the entry to the exit of the map.

    Uses a breadth-first search: it visits every cell one step away from
    the entry, then every cell two steps away, and so on. The first time
    the exit is reached is therefore by a shortest path.

    The cells of the path, entry and exit included, get path = True and
    every other cell gets path = False.

    Args:
        maze_map: map with an entry, an exit and its walls already opened.

    Returns:
        The path as letters "N", "S", "E" and "W", one for each step from
        the entry to the exit. It is empty if the entry is the exit.

    Raises:
        ValueError: if the map has no entry or no exit, or if the exit
            cannot be reached from the entry.
    """
    if maze_map.entry is None or maze_map.exit is None:
        raise ValueError("The map needs an entry and an exit.")
    entry: Position = maze_map.entry
    exit: Position = maze_map.exit

    # cell -> (cell it was reached from, direction of that step)
    came_from: Dict[Position, Tuple[Position, str]] = {}
    queue: Deque[Position] = deque([entry])
    while queue:
        current = queue.popleft()
        if current == exit:
            break
        row, col = current
        for direction, (row_delta, col_delta, _) in DIRECTIONS.items():
            if getattr(maze_map.cell(row, col), direction):
                continue
            neighbour = (row + row_delta, col + col_delta)
            if neighbour == entry or neighbour in came_from:
                continue
            came_from[neighbour] = (current, direction)
            queue.append(neighbour)
    if exit != entry and exit not in came_from:
        raise ValueError("The exit cannot be reached from the entry.")

    for cells in maze_map.grid:
        for cell in cells:
            cell.path = False
    # Walk back from the exit to the entry, then reverse the letters.
    letters: List[str] = []
    current = exit
    maze_map.cell(*current).path = True
    while current != entry:
        current, direction = came_from[current]
        letters.append(direction)
        maze_map.cell(*current).path = True
    return "".join(reversed(letters))
