# Task 8 — Output

Implementação da Task 8 do [TASKS.md](TASKS.md): o desenho do labirinto no terminal, em ASCII, mostrando paredes, entrada, saída, o "42" e, opcionalmente, o caminho. Não havia um `TASK_8.md`, então segui o `TASKS.md` e o capítulo V do subject.

## Resultado

- 77 testes, 77 passando (68 das Tasks 1 a 7 + 9 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- `a_maze_ing.py config.txt` agora desenha o labirinto no terminal, com o caminho, e imprime as letras do caminho embaixo.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/renderer.py` | novo: `render_maze`, `cell_text` e as constantes dos caracteres |
| `src/main.py` | imprime o desenho no lugar do `pprint` de cada célula |
| `tests/test_renderer.py` | novo: 9 testes |

Nada dentro de `src/mazegen/` foi alterado.

## O desenho

Mapa 5x7 (o do `config.txt` atual), entrada `0,0`, saída `4,6`, seed 2, `PERFECT=False`:

```
+---+---+---+---+---+
| E   o   o |       |
+   +   +   +   +   +
|   |   | o   o |   |
+   +   +---+   +   +
|           | o   o |
+   +   +   +---+   +
|       |   |     o |
+---+---+   +   +   +
|           |     o |
+   +   +   +   +   +
|       |       | o |
+   +---+---+---+   +
|                 X |
+---+---+---+---+---+
```

| Símbolo | Significado |
|---------|-------------|
| `---` e `\|` | parede fechada |
| espaço no lugar da parede | parede aberta |
| `+` | canto entre células; sempre desenhado |
| ` E ` | entrada |
| ` X ` | saída |
| `###` | célula do "42" |
| ` o ` | célula do caminho mais curto (só com `show_path=True`) |

Num mapa grande o "42" aparece no centro. Trecho do 20x15 com seed 42:

```
+   +---+---+   +---+   +---+   +---+   +---+---+---+   +
| o   o   o         |###|   |###|   |###|###|###|   |
+   +---+   +---+   +---+   +---+   +---+---+---+   +
| o     | o |       |###|   |###|           |###|
+---+   +   +   +---+---+---+---+   +---+---+---+---+
    |   | o | o   o |###|###|###|   |###|###|###|
+   +   +   +   +   +---+---+---+   +---+---+---+   +
    |   | o   o | o   o   o |###|   |###|
+   +   +   +---+   +---+   +---+   +---+---+---+---+
        |   |       | o   o |###|   |###|###|###| o
```

## Código

```python
def cell_text(maze_map: Map, position: Position, show_path: bool) -> str:
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


def render_maze(maze_map: Map, show_path: bool = False) -> str:
    lines: List[str] = []
    top = CORNER
    for cell in maze_map.grid[0]:
        top += (CLOSED_HORIZONTAL if cell.N else OPEN_HORIZONTAL) + CORNER
    lines.append(top)
    for row in range(maze_map.rows):
        first = maze_map.cell(row, 0)
        middle = CLOSED_VERTICAL if first.W else OPEN_VERTICAL
        bottom = CORNER
        for col in range(maze_map.cols):
            cell = maze_map.cell(row, col)
            middle += cell_text(maze_map, (row, col), show_path)
            middle += CLOSED_VERTICAL if cell.E else OPEN_VERTICAL
            bottom += CLOSED_HORIZONTAL if cell.S else OPEN_HORIZONTAL
            bottom += CORNER
        lines.append(middle)
        lines.append(bottom)
    return "\n".join(lines)
```

## Como funciona

### Uma célula ocupa 4 colunas e 2 linhas

Cada célula é desenhada assim, e os cantos e paredes são compartilhados com as vizinhas:

```
+---+     <- parede norte (é a parede sul da célula de cima)
| o |     <- parede oeste, 3 caracteres de conteúdo, parede leste
+---+     <- parede sul
```

Por isso um mapa de `R` linhas por `C` colunas vira um desenho de `2R + 1` linhas por `4C + 1` caracteres.

### As linhas do desenho

1. **A primeira linha** é feita com a parede **norte** de cada célula da primeira fileira.
2. **Para cada fileira do mapa**, duas linhas:
   - `middle`: começa com a parede **oeste** da primeira célula; depois, para cada célula, o conteúdo e a parede **leste**.
   - `bottom`: para cada célula, a parede **sul**.

Só quatro tipos de parede são lidos: o norte da primeira fileira, o oeste da primeira coluna, e o leste e o sul de todas as células. Isso basta porque as vizinhas sempre concordam sobre a parede entre elas (Task 1): a parede norte de uma célula já foi desenhada como a parede sul da célula de cima.

### O conteúdo da célula

`cell_text` decide os 3 caracteres do meio, nesta ordem de prioridade: entrada, saída, "42", caminho, vazio.

A entrada e a saída vêm antes do caminho porque também são células do caminho: sem essa ordem, mostrar o caminho apagaria o `E` e o `X`.

O "42" é lido de `cell.is_42` e o caminho de `cell.path`. O renderer não calcula nada: só mostra o que o `Map` já guarda.

## Decisões que tomei

- **A função devolve o texto; não imprime.** Quem chama faz o `print`. Assim o desenho pode ser testado como uma string comum, e o menu da Task 9 decide quando e onde mostrar.
- **O arquivo fica em `src/renderer.py`, fora de `mazegen`.** A Task 7 pede que o `mazegen` não dependa do terminal. O renderer depende do `mazegen`, e não o contrário.
- **Recebe o `Map`, não o `MazeGenerator`.** Tudo o que o desenho precisa está no `Map` (paredes, entrada, saída, `is_42`, `path`).
- **`show_path` é `False` por padrão.** O `TASKS.md` diz que o caminho é opcional. O `main.py` passa `True`, para já dar para ver o caminho; o liga/desliga é a Task 9.
- **Só ASCII, sem cores.** Trocar a cor das paredes é uma interação da Task 9. Os caracteres estão em constantes no topo do arquivo, que é onde a cor vai entrar.
- **Cada parede é desenhada a partir da própria célula**, inclusive as bordas. Se um dia uma borda estiver aberta por engano, o desenho mostra.

## Mudanças no `main.py`

- O laço que fazia `pprint(vars(cell))` de cada célula foi trocado por `print(render_maze(generator.maze_map, show_path=True))`.
- Removi o `import pprint` e a linha comentada `# pprint(config, sort_dicts=False)`, que ficaram sem uso. Era o teu código de depuração: se ainda precisares dele, é só repor.
- A linha com as letras do caminho continua sendo impressa depois do desenho.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "o desenho bate com o arquivo de saída e o '42' é visível".

| Critério | Teste que cobre |
|----------|-----------------|
| O desenho bate com o arquivo de saída | `test_drawing_matches_the_output_file` |
| O "42" é visível | `test_42_is_visible_in_the_right_cells` |
| Mostra a entrada e a saída | `test_entry_and_exit_are_in_their_cells` |
| O caminho é opcional | `test_path_is_hidden_by_default`, `test_path_marks_the_cells_between_entry_and_exit` |

`test_drawing_matches_the_output_file` faz o caminho inverso do renderer: lê o desenho caractere por caractere, reconstrói as quatro paredes de cada célula e as converte em dígitos hexadecimais. O resultado tem de ser igual às linhas da grade do arquivo de saída. Roda em 10 labirintos 20x15 (5 seeds em cada modo), com e sem o caminho.

`test_small_map_drawn_by_hand` compara o desenho inteiro de um mapa 2x3 com o esperado, escrito à mão:

```
+---+---+---+
| E   o   o |
+---+---+   +
|   |   | X |
+---+---+---+
```

Testes além dos critérios:

- `test_drawing_has_the_size_of_the_map`: `2R + 1` linhas, todas com `4C + 1` caracteres.
- `test_showing_the_path_changes_nothing_else`: com e sem caminho, a única diferença são os `o`.
- `test_rendering_does_not_change_the_map`: desenhar não altera paredes nem marcas de caminho.

## Como rodar

Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe a_maze_ing.py config.txt

.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- **Largura do terminal.** O desenho usa 4 caracteres por coluna do mapa. Um labirinto de 20 colunas ocupa 81 caracteres; um de 50 ocupa 201 e quebra de linha na maioria dos terminais, o que desmonta o desenho. Não tratei isso.
- **O caminho mostra as células, não a direção.** Em corredores largos do modo não-perfeito, dois trechos do caminho podem ficar lado a lado e a ordem não é evidente só pelo desenho. As letras impressas embaixo tiram a dúvida.
- **A docstring do `main()`** ainda diz que ele só mostra o dicionário do config. Deixei para a Task 9, que reescreve o `main.py`.
