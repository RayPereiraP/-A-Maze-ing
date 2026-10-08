*This project has been created as part of the 42 curriculum by LOGIN_HERE.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration
file, generates a random maze, writes it to a file with one hexadecimal
digit per cell, and draws it in the terminal with a small interactive menu.

The goal of the project is to learn how a computer builds structure out of
randomness: a perfect maze is a spanning tree of a grid, and a shortest
path is a breadth-first search on it.

What the program does:

- generates a **perfect** maze (exactly one path between any two cells) or
  a **board with loops**, usable by a Pac-Man-like game;
- gives the same maze again when the same seed is used;
- draws a "42" in the centre of the maze with fully closed cells;
- finds the shortest path from the entry to the exit;
- shows the maze in the terminal, where the user can generate another
  maze, show or hide the path and change the colour of the walls;
- provides the generator as a reusable package, `mazegen`.

Only the mandatory part of the subject is implemented.

## Instructions

### Requirements

- Python 3.10 or later.
- Running the program needs nothing else: it only uses the standard
  library. `flake8`, `mypy` and `build` are needed for the lint and for
  building the package.

### Install

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
```

### Run

```sh
make run                          # python3 a_maze_ing.py config.txt
python3 a_maze_ing.py config.txt  # the same, without make
make run CONFIG=other.txt         # another configuration file
```

The program writes the output file, draws the maze and waits for a choice.
Here, a maze of 5 by 3 cells with the path shown:

```
+---+---+---+---+---+
| E   o             |
+   +   +---+   +   +
|   | o   o   o |   |
+   +---+   +   +   +
|           | o   X |
+---+---+---+---+---+
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
Choice? (1-4):
```

| Symbol | Meaning |
|--------|---------|
| `---` and `\|` | closed wall |
| ` E ` | entry |
| ` X ` | exit |
| `###` | cell of the "42" pattern |
| ` o ` | cell of the shortest path, when it is shown |

When a seed is given, "Re-generate" uses the next seed (seed + 1, seed + 2,
and so on), so a run is still reproducible. Every new maze is also written
to the output file.

### Other rules of the Makefile

| Rule | What it does |
|------|--------------|
| `make debug` | runs the program inside `pdb` |
| `make lint` | `flake8 .` and `mypy .` with the flags of the subject |
| `make lint-strict` | `flake8 .` and `mypy . --strict` |
| `make build` | builds `mazegen-*.whl` and `mazegen-*.tar.gz` at the root |
| `make clean` | removes `__pycache__`, `.mypy_cache` and the build folders |

### Tests

```sh
python3 -m unittest discover -s tests -t .
```

### Checking an output file

`maze_analyzer.py`, provided with the subject, checks that an output file is
coherent and tells whether the maze is perfect or a playable board:

```sh
python3 maze_analyzer.py maze.txt
```

## Configuration file

One `KEY=VALUE` pair per line. Blank lines and lines starting with `#` are
ignored. Spaces around the key and the value are ignored.

| Key | Mandatory | Value | Example |
|-----|-----------|-------|---------|
| `WIDTH` | yes | number of columns, greater than zero | `WIDTH=20` |
| `HEIGHT` | yes | number of rows, greater than zero | `HEIGHT=15` |
| `ENTRY` | yes | `x,y` of the entry, inside the maze | `ENTRY=0,0` |
| `EXIT` | yes | `x,y` of the exit, inside the maze, different from the entry | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | name of the file to write | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True` or `False`, in any letter case | `PERFECT=True` |
| `SEED` | no | an integer; without it each run gives a different maze | `SEED=42` |

`x` is the column and `y` is the row, both starting at zero, with `0,0` at
the top-left corner.

The program stops with a clear message, and never with a traceback, when
the file cannot be read, a line is not `KEY=VALUE`, a key appears twice, a
mandatory key is missing or a value is not valid. Any other key is accepted
and ignored.

The default configuration file is [config.txt](config.txt):

```
# Maze dimensions in cells
WIDTH=10
HEIGHT=10

# Coordinates (x,y), starting at zero
ENTRY=0,0
EXIT=9,9

OUTPUT_FILE=maze.txt
PERFECT=False

# Optional seed for future reproducible generation
SEED=1
```

## Output file

One hexadecimal digit per cell, one row of the maze per line. Each bit of
the digit is one wall; 1 means the wall is closed.

| Wall | Bit | Value |
|------|-----|-------|
| North | 0 | 1 |
| East | 1 | 2 |
| South | 2 | 4 |
| West | 3 | 8 |

For example, `9` is 1 + 8: the north and the west walls are closed.

After the rows come an empty line, the entry as `x,y`, the exit as `x,y`
and the shortest path as the letters `N`, `E`, `S` and `W`. Every line ends
with `\n`.

## The maze generation algorithm

### Perfect maze: depth-first search with backtracking

Also known as the *recursive backtracker*. Every wall starts closed.

1. Start at the entry and mark it as visited.
2. From the current cell, pick at random a neighbour that was never
   visited, open the wall between the two and move there.
3. When the current cell has no unvisited neighbour, step back to the
   previous cell.
4. Stop when the walk has stepped back all the way to the start.

A wall is only ever opened towards a cell that was never visited, so no
loop can appear, and the walk only ends when every cell was reached: the
result is a perfect maze. The cells of the "42" are never visited, so they
stay fully closed, and the outer borders stay closed because walls are only
opened between two cells.

The steps back use an explicit list as a stack, not recursive calls, so a
big maze cannot hit the recursion limit of Python.

### Board with loops (`PERFECT=False`)

It starts from the perfect maze and then opens more walls. Every closed
wall between two normal cells is looked at once, in random order, and is
opened if:

- the maze still has fewer than two loops, **or** one of the two cells is a
  dead-end;
- **and** opening it would not create an open area of 3x3 cells.

The maze is already connected, so each wall opened this way adds exactly
one loop. This removes most dead-ends and guarantees at least two
independent routes.

### Shortest path: breadth-first search

The search visits the cells one step away from the entry, then two steps
away, and so on. The first time it reaches the exit is therefore by a
shortest path.

### Why this algorithm

- **It is correct by construction.** The rule "only open a wall towards an
  unvisited cell" is the whole proof that the maze is perfect; there is
  nothing to check or repair afterwards.
- **It is simple to explain and to change.** One stack and one set of
  visited cells, in about twenty lines.
- **It is easy to make reproducible.** All the randomness comes from one
  `random.Random(seed)`.
- **It gives long, winding corridors**, which make a maze that is pleasant
  to look at and not trivial to solve.
- **It is fast:** each cell is entered once and left once.

The price is that these mazes have long corridors and few branches, so in
perfect mode the solution tends to be long. Prim's or Kruskal's algorithms
give more, shorter dead-ends; they need more bookkeeping (a frontier list
or a union-find structure) for the same guarantee.

## Reusable code: the `mazegen` package

Everything in [src/mazegen/](src/mazegen/) is reusable: the generation, the
"42" pattern, the shortest path and the output file. It does not depend on
the configuration parser, on the terminal drawing or on the menu, which are
the application.

It is distributed as a package at the root of the repository:
`mazegen-1.0.0-py3-none-any.whl` and `mazegen-1.0.0.tar.gz`. To build it
again from the sources:

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
make build
```

### Install

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen import MazeGenerator

generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19))
print(generator.path)
```

The maze is generated when the object is created. Every position is
`(row, col)`, with `(0, 0)` at the top-left corner: the row grows towards
the south and the column towards the east.

### Parameters

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

### The generated structure

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

### The solution

`generator.path` is the shortest path from the entry to the exit, as a
string of the letters `N`, `E`, `S` and `W`. The cells of this path also
have `cell.path` set to `True`.

### Writing the maze to a file

```python
generator.write("maze.txt")
```

The entry and the exit are written as `x,y`, that is, column first.

### License

The code is under the MIT license: see [LICENSE.md](LICENSE.md). It may be
used, copied, modified and distributed, as long as the copyright notice and
the license text are kept.

## Project structure

| Path | Content |
|------|---------|
| `a_maze_ing.py` | entry point required by the subject |
| `src/main.py` | the program: parser, generator, output file, menu |
| `src/parser.py` | reads and validates the configuration file |
| `src/renderer.py` | draws a maze as text |
| `src/mazegen/` | the reusable package |
| `tests/` | unit tests (`unittest`) |
| `tasks/` | the task list and one report per task |
| `Makefile`, `requirements.txt`, `setup.cfg` | install, run, lint |
| `pyproject.toml`, `MANIFEST.in` | how the package is built |

## Team and project management

### Team

| Member | Role |
|--------|------|
| LOGIN_HERE | everything: design, code, tests, documentation |

### Planning

The project was cut into 14 tasks, each with what it depends on and a
sentence saying when it is done. The list is in
[tasks/TASKS.md](tasks/TASKS.md). A task was only started when the one
before it was finished.

| Tasks | Part |
|-------|------|
| 0 to 7 | parser, grid, "42" pattern, perfect maze, shortest path, output file, loops mode, `MazeGenerator` class |
| 8 and 9 | terminal drawing, interactive menu |
| 10 to 13 | Makefile and lint, package, license, README |

How it evolved:

- The order of the list was kept from the start to the end.
- The menu first printed each new maze below the previous one; clearing
  the screen before each drawing was added after trying it.
- Building the package (task 11) forced a change in code that was already
  done: the imports inside `mazegen` became relative, because the installed
  package is not called `src.mazegen`.

### What worked well

- One small task at a time, each ending with tests and a written report,
  kept every step small enough to understand before moving on.
- Keeping the generator apart from the program from task 7 on made the
  package of task 11 almost only configuration.
- Tests that read the result back (the drawing converted to the digits of
  the output file, the path walked cell by cell) caught mistakes that
  looking at the screen would not.

### What could be improved

- The drawing uses four characters per column and does not adapt to the
  width of the terminal: a wide maze wraps and becomes unreadable.
- The path is drawn as marked cells, without its direction.
- The package prints the "42" warning on stderr by itself; a library
  should rather let the caller decide what to do with it.
- The development machine had no `make`, so the Makefile and the package
  build were only tested inside a Linux container.

### Tools

- Python 3.10, `unittest`, `flake8`, `mypy`.
- `setuptools` and `build` for the package.
- Git, Visual Studio Code.
- Docker, as a Linux environment to run `make` and to build and install
  the package in a clean virtualenv.
- Claude Code (see below).

## Resources

### References

- Jamis Buck, *Maze Generation: Recursive Backtracking* —
  <https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking>
- Jamis Buck, *Mazes for Programmers*, The Pragmatic Bookshelf, 2015.
- Wikipedia, *Maze generation algorithm* —
  <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- Wikipedia, *Breadth-first search* —
  <https://en.wikipedia.org/wiki/Breadth-first_search>
- Wikipedia, *Spanning tree* —
  <https://en.wikipedia.org/wiki/Spanning_tree>
- Wikipedia, *ANSI escape code* —
  <https://en.wikipedia.org/wiki/ANSI_escape_code>
- Python Packaging User Guide, *Packaging Python Projects* —
  <https://packaging.python.org/en/latest/tutorials/packaging-projects/>
- PEP 257, *Docstring Conventions* — <https://peps.python.org/pep-0257/>
- mypy documentation — <https://mypy.readthedocs.io/>
- flake8 documentation — <https://flake8.pycqa.org/>
- GNU Make manual — <https://www.gnu.org/software/make/manual/>
- Choose a License — <https://choosealicense.com/>

### How AI was used

An AI coding assistant (Claude Code) was used during the project, one task
at a time.

- **Code:** for each task, the assistant wrote a first version of the code
  and of its tests from the description of the task. This covers the
  application (`src/main.py`, `src/renderer.py`) and the `mazegen`
  package.
- **Reports:** for each task, the assistant wrote a report
  (`tasks/TASK_N_OUTPUT.md`) explaining what was done, why, how it was
  checked and what was left open. These reports were the material used to
  study each part before going on to the next task.
- **Delivery:** the Makefile, the lint configuration, the packaging files,
  the proposal of license with its comparison, and the draft of this
  README.

What stayed with the author: deciding the order and the limits of each
task, accepting or sending back each result (for example, asking for the
screen to be cleared between drawings), choosing the license, and marking
a task as done only after understanding it.
