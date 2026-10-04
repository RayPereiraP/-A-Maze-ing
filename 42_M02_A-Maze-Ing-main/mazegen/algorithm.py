from random import shuffle, choice, randint
from .utils import Maze, Directions
from typing import Optional


# do it as ABC interface and then inherit concrete algorithms?

class Algorithm:
    """Class implementing the recursive backtracking algorithm"""
    def __init__(self, maze: Maze, perfect: bool) -> None:
        self._maze: Maze = maze
        self._perfect: bool = perfect
        self._path: list[Directions] = []

    def backtracker(self, x: int, y: int,
                    entry_dir: Optional[Directions] = None) -> bool:
        """Run the recursive backtracking algorithm to add paths to maze"""
        cur_cell = self._maze.get_cell(x, y)
        cur_cell["visited"] = True
        on_path = False
        if self._maze.exit == (x, y):
            on_path = True
        dirs = list(Directions)
        shuffle(dirs)
        neighbors = self._maze.get_neighbors(x, y)
        for d in dirs:
            try:
                next_cell = self._maze.get_cell(*neighbors[d.value])
            except KeyError:
                continue
            if not next_cell["visited"] and not next_cell["pattern"]:
                cur_cell[d.value] = False
                next_cell[self.opposite_direction(d)] = False
                if self.backtracker(*neighbors[d.value], d):
                    on_path = True
        if not self._perfect and randint(1, 4) == 4:
            self._punch_hole(cur_cell, neighbors)
        if self._perfect and on_path and entry_dir:
            self._path.append(entry_dir)
        if not self._perfect and (x, y) == self._maze.entry:
            impf_path = self._solve_path(x, y)
            impf_path.reverse()
            self._path = impf_path
        return on_path

    def _punch_hole(self, cur_cell: dict[str, bool],
                    neighbors: dict[str, tuple[int, int]]) -> None:
        """Create hole in a random wall from current cell while generating
        an imperfect maze"""
        dirs = list(Directions)
        rand_dir = choice(dirs)
        try:
            rand_cell = self._maze.get_cell(*neighbors[rand_dir.value])
        except KeyError:
            return
        if not rand_cell["pattern"]:
            cur_cell[rand_dir.value] = False
            rand_cell[self.opposite_direction(rand_dir)] = False

    def _solve_path(self, x: int, y: int) -> list[Directions]:
        """Find shortest path in an imperfect maze.
        For a perfect maze, path is saved during generation instead."""
        for w in range(self._maze.width):
            for h in range(self._maze.height):
                self._maze.get_cell(w, h)["visited"] = False
        active_cells: list[tuple[int, int, list[Directions]]] = [(x, y, [])]
        while True:
            new_cells: list[tuple[int, int, list[Directions]]] = []
            for i in range(len(active_cells)):
                cell_x, cell_y, cell_path = active_cells[i]
                if self._maze.exit == (cell_x, cell_y):
                    return cell_path
                cell = self._maze.get_cell(cell_x, cell_y)
                cell["visited"] = True
                neighbors = self._maze.get_neighbors(cell_x, cell_y)
                for n_dir, n_cell in neighbors.items():
                    if (not cell[n_dir] and
                            not self._maze.get_cell(*n_cell)["visited"]):
                        new_path = cell_path.copy()
                        new_path.append(Directions(n_dir))
                        not_in_new = True
                        for cell_to_check in new_cells:
                            if (cell_to_check[0], cell_to_check[1]) == n_cell:
                                not_in_new = False
                                break
                        if not_in_new:
                            new_cells.append((*n_cell, new_path))
            active_cells = [c for c in new_cells
                            if not self._maze.get_cell(c[0], c[1])["visited"]]

        """if self._maze.exit == (x, y):
            return path
        cur_cell = self._maze.get_cell(x, y)
        neighbors = self._maze.get_neighbors(x, y)
        if path is None:
            path = []
            path_cells = [(x, y)]
        for d in Directions:
            if not cur_cell[d.value] and neighbors[d.value] not in path_cells:
                path.append(d)
                path_cells.append(neighbors[d.value])
                new_path = self._solve_path(*neighbors[d.value],
                                            path_cells, path)
                if new_path:
                    return new_path
                else:
                    path.pop()
                    path_cells.pop()"""

    def get_path(self) -> str:
        """Get the path from entry to exit in string format"""
        path = [d.value for d in self._path]
        path.reverse()
        return "".join(path)

    @staticmethod
    def opposite_direction(d: Directions) -> str:
        """Get the opposite direction to a given direction"""
        match d:
            case Directions.N:
                return "S"
            case Directions.E:
                return "W"
            case Directions.S:
                return "N"
            case Directions.W:
                return "E"
