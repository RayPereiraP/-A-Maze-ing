# Task 1 — Output

Implementação das classes `Cell` e `Map`, pedidas em [TASK_1.md](TASK_1.md) como `Celula` e `Mapa`. O código está em inglês, como o resto do projeto.

## Resultado

- 12 testes escritos, 12 passando.
- `flake8` sem avisos.
- `mypy` sem erros com as flags do subject, e também com `--strict`.
- O programa existente (`a_maze_ing.py config.txt`) continua funcionando igual: ele ainda não usa as classes novas.

## Resposta à Open Question

A linguagem é **Python**. O projeto já existe e é Python 3.10+ (exigência do subject), então segui as convenções do `src/parser.py`: type hints em tudo, docstrings e linhas de até 79 caracteres.

## Nomes: da task para o código

| Na task | No código |
|---------|-----------|
| `Celula` | `Cell`, em `mazegen/cell.py` |
| `Mapa` | `Map`, em `mazegen/map.py` |
| indicador de caminho | `Cell.path` |
| matriz de células | `Map.grid` |
| linhas, colunas | `Map.rows`, `Map.cols` |
| acessar célula por posição | `Map.cell(row, col)` |
| abrir parede | `Map.open_wall(row, col, direction)` |

## Arquivos criados

| Arquivo | Conteúdo |
|---------|----------|
| `mazegen/cell.py` | classe `Cell` |
| `mazegen/map.py` | classe `Map` e a tabela `DIRECTIONS` |
| `mazegen/__init__.py` | exporta `Cell` e `Map` |
| `tests/test_map.py` | os 12 testes |
| `tests/__init__.py` | vazio; só torna `tests` um pacote |

Nenhum arquivo que já existia antes da task foi alterado.

## Código

### `mazegen/cell.py`

```python
"""Maze cell: stores only the state of its own walls."""


class Cell:
    """A cell with four walls and a path marker.

    For each wall, True means the wall is closed and False means it is open.
    The cell does not know where it is in the grid or who its neighbours are.
    """

    def __init__(self) -> None:
        """Create the cell with its four walls closed and off the path."""
        self.N: bool = True
        self.S: bool = True
        self.E: bool = True
        self.W: bool = True
        self.path: bool = False
```

A classe não tem nenhum método além do construtor. Ela é só um conjunto de cinco booleanos: quem decide o que fazer com eles é o `Map`.

### `mazegen/map.py`

```python
"""Maze map: the grid of cells and the neighbourhood rules."""

from typing import Dict, List, Tuple

from mazegen.cell import Cell


# direction -> (row change, column change, opposite wall)
DIRECTIONS: Dict[str, Tuple[int, int, str]] = {
    "N": (-1, 0, "S"),
    "S": (1, 0, "N"),
    "E": (0, 1, "W"),
    "W": (0, -1, "E"),
}


class Map:
    """Grid of cells; the only one that knows positions and neighbours.

    A cell position is always (row, col), with (0, 0) at the top-left corner.
    The row grows towards the south and the column towards the east.
    """

    def __init__(self, rows: int, cols: int) -> None:
        """Create the grid with rows x cols new cells.

        Args:
            rows: number of rows in the grid.
            cols: number of columns in the grid.

        Raises:
            ValueError: if either dimension is smaller than 1.
        """
        if rows < 1 or cols < 1:
            raise ValueError("The map needs at least 1 row and 1 column.")
        self.rows: int = rows
        self.cols: int = cols
        self.grid: List[List[Cell]] = [
            [Cell() for _ in range(cols)] for _ in range(rows)
        ]

    def contains(self, row: int, col: int) -> bool:
        """Tell whether the position (row, col) exists in the grid."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def cell(self, row: int, col: int) -> Cell:
        """Return the cell at position (row, col).

        Raises:
            IndexError: if the position is outside the grid.
        """
        if not self.contains(row, col):
            raise IndexError(f"Position ({row}, {col}) is outside the map.")
        return self.grid[row][col]

    def open_wall(self, row: int, col: int, direction: str) -> bool:
        """Open the wall between the cell (row, col) and its neighbour.

        Changes both cells: the `direction` wall of the origin and the
        opposite wall of the neighbour. If the neighbour is outside the grid
        (border), nothing is changed.

        Args:
            row: row of the origin cell.
            col: column of the origin cell.
            direction: one of the letters "N", "S", "E" or "W".

        Returns:
            True if the wall was opened, False if the direction points
            outside the grid.

        Raises:
            ValueError: if the direction is not one of the four letters.
            IndexError: if the origin cell is outside the grid.
        """
        if direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction!r}.")
        origin = self.cell(row, col)
        row_delta, col_delta, opposite = DIRECTIONS[direction]
        neighbour_row = row + row_delta
        neighbour_col = col + col_delta
        if not self.contains(neighbour_row, neighbour_col):
            return False
        neighbour = self.grid[neighbour_row][neighbour_col]
        setattr(origin, direction, False)
        setattr(neighbour, opposite, False)
        return True
```

### `mazegen/__init__.py`

```python
"""Reusable maze generation module."""

from mazegen.cell import Cell
from mazegen.map import Map

__all__ = ["Cell", "Map"]
```

## Como funciona

### A tabela `DIRECTIONS`

Toda a lógica de vizinhança e de direção oposta está nesta tabela. Cada direção guarda três coisas: quanto a linha muda, quanto a coluna muda, e qual parede da vizinha fica encostada na parede da origem.

| Direção | Linha | Coluna | Parede oposta |
|---------|-------|--------|---------------|
| `N` | −1 | 0 | `S` |
| `S` | +1 | 0 | `N` |
| `E` | 0 | +1 | `W` |
| `W` | 0 | −1 | `E` |

O norte diminui a linha porque a linha 0 é a de cima, igual ao arquivo de saída do subject, que é escrito de cima para baixo.

### `open_wall`, passo a passo

Exemplo: `maze_map.open_wall(1, 1, "E")` num mapa 3x3.

1. `"E"` existe em `DIRECTIONS`, então a direção é válida.
2. `origin` é a célula `(1, 1)`.
3. A tabela devolve `(0, +1, "W")`.
4. A vizinha fica em `(1 + 0, 1 + 1)`, ou seja, `(1, 2)`.
5. `(1, 2)` está dentro da grade, então a operação segue.
6. `setattr(origin, "E", False)` é o mesmo que escrever `origin.E = False`.
7. `setattr(neighbour, "W", False)` é o mesmo que escrever `neighbour.W = False`.

O `setattr` permite usar a letra da direção como nome do atributo. Sem ele, seriam necessários quatro `if`/`elif` para a origem e mais quatro para a vizinha.

A ordem das verificações é o que garante que nada seja alterado em caso de erro: as duas escritas só acontecem depois de todas as checagens passarem.

## Decisões que tomei

A task deixava algumas escolhas em aberto. Estas são as que fiz e o motivo de cada uma.

- **Borda: a operação é ignorada e devolve `False`.** A task permitia rejeitar ou ignorar. Escolhi devolver `True`/`False` porque o gerador da Task 3 vai tentar direções aleatórias, e bater na borda será um caso normal, não um erro.
- **Direção desconhecida levanta `ValueError`.** Diferente da borda, isso é um erro de quem chamou. Sem essa checagem, `open_wall(1, 1, "path")` alteraria o indicador de caminho pelo `setattr`.
- **Posição fora da grade levanta `IndexError`.** Em Python, `grid[-1]` não dá erro: devolve a última linha. Por isso `cell()` verifica os limites antes de acessar a matriz.
- **Dimensões menores que 1 levantam `ValueError`.** Um mapa `0x5` não teria nenhuma célula.
- **Atributos de parede em maiúscula (`N`, `S`, `E`, `W`).** São as mesmas letras da task e do caminho no arquivo de saída, e assim a letra da direção é o próprio nome do atributo.
- **Classe `Map`, variáveis `maze_map`.** `map` em minúscula já é uma função do Python. Nos testes a variável se chama `maze_map` para não escondê-la.
- **Pasta `mazegen/` em vez de `src/`.** O subject exige que o módulo reutilizável se chame `mazegen`, então o código do labirinto já nasce lá. O parser continua em `src/`.

## Ponto de atenção para as próximas tasks

O `Map` usa `(row, col)`. O config e o arquivo de saída do subject usam `(x, y)`, onde `x` é a coluna e `y` é a linha. A entrada `ENTRY=3,0` é a célula `maze_map.cell(0, 3)`. A conversão vai precisar ser feita quando o gerador receber a entrada e a saída.

## Critérios de aceitação

| Critério | Teste que cobre |
|----------|-----------------|
| Célula nova tem as 4 paredes `True` e caminho `False` | `test_initial_state` |
| Célula não tem atributo que dependa de posição | `test_does_not_know_position` |
| Mapa `R x C` tem `R` arrays de `C` células | `test_dimensions` |
| Abrir uma parede altera a origem e a parede oposta da vizinha, nas 4 direções | `test_open_in_four_directions` |
| Abrir uma parede não altera nenhuma outra parede | `test_open_in_four_directions` |
| Abrir em direção à borda não altera nada | `test_open_towards_border` |

Os testes de abertura fotografam todas as paredes do mapa antes e depois, e comparam a lista de paredes que mudaram com as duas esperadas. Isso prova que mudaram exatamente duas, e não só que as duas certas mudaram.

Testes além dos critérios:

- `test_cells_are_independent`: as 15 células de um mapa 3x5 são objetos diferentes.
- `test_access_by_position` e `test_access_outside_grid`: o acesso por posição.
- `test_open_does_not_mark_path`: abrir parede não mexe no indicador de caminho.
- `test_invalid_dimensions`, `test_invalid_direction`, `test_origin_outside_grid`: os três erros.

## Como rodar

Não há `python` no PATH desta máquina, então usei o Python 3.10 que já estava em `tmp/parser-runtime/`. Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 mazegen tests src a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy mazegen tests src a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pendência

O `.gitignore` atual só ignora `/src/__pycache__`. Rodar os testes cria `mazegen/__pycache__` e `tests/__pycache__`, que hoje aparecem como arquivos novos no git. Não alterei o `.gitignore` porque isso está previsto na Task 10; trocar a linha por `__pycache__/` resolve.
