# mazegen

Maze generator of the A-Maze-ing project, as a module that can be reused
in another project. It only needs the Python standard library (3.10+).

## Install

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

## Basic example

```python
from mazegen import MazeGenerator

generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19))
print(generator.path)
```

The maze is generated when the object is created. Every position is
`(row, col)`, with `(0, 0)` at the top-left corner: the row grows towards
the south and the column towards the east.

## Parameters

```python
generator = MazeGenerator(
    rows=15,            # height of the maze, in cells
    cols=20,            # width of the maze, in cells
    entry=(0, 0),       # (row, col) of the entry
    exit=(14, 19),      # (row, col) of the exit
    perfect=True,       # True: one single path between any two cells
                        # False (default): a board with loops
    seed=42,            # the same seed always gives the same maze
                        # None (default): a different maze each time
)
```

A `ValueError` is raised if a dimension is smaller than 1, if the entry or
the exit is outside the maze, or if they are the same cell.

To get another maze from the same object, change `seed` and call
`generate()`:

```python
generator.seed = 43
generator.generate()
```

## The generated structure

`generator.maze_map` is a `Map`: a grid of `Cell` objects.

```python
maze_map = generator.maze_map
print(maze_map.rows, maze_map.cols)

cell = maze_map.cell(0, 0)      # the cell at row 0, column 0
print(cell.N, cell.E, cell.S, cell.W)   # True = wall closed, False = open
print(cell.is_42)               # True if the cell draws the "42"
print(cell.path)                # True if the cell is on the shortest path

for row in maze_map.grid:       # the whole grid, row by row
    for cell in row:
        ...
```

Two neighbouring cells always agree on the wall between them. The cells of
the "42" pattern, drawn in the centre of the maze, are fully closed. The
pattern is left out, with a message on stderr, when the maze is smaller
than 9 columns by 7 rows or when the entry or the exit sits on it.

## The solution

`generator.path` is the shortest path from the entry to the exit, as a
string of the letters `N`, `E`, `S` and `W`:

```python
print(generator.path)           # for example "EESSEN..."
```

The cells of this path also have `cell.path` set to `True`.

## Writing the maze to a file

```python
generator.write("maze.txt")
```

The file has one hexadecimal digit per cell (bit 0 = north, 1 = east,
2 = south, 3 = west; a bit set to 1 is a closed wall), one row per line,
then an empty line, the entry, the exit and the path. The entry and the
exit are written as `x,y`, that is, column first.

## License

MIT: the module may be used, copied, modified and distributed, as long as
the copyright notice and the license text are kept. The full text is in
the `LICENSE.md` file that comes with the package.
