# Task 3 — Output

Implementação da Task 3 do [TASKS.md](TASKS.md): a geração do labirinto perfeito, com seed. Não havia um `TASK_3.md`, então segui a descrição e o critério "Pronta quando" do `TASKS.md`.

## Resultado

- 29 testes, 29 passando (20 das Tasks 1 e 2 + 9 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- O `maze_analyzer.py` do subject, rodado sobre um labirinto 20x15 gerado com seed 42, respondeu: `PERFECT maze: a single path, no loop`, com as 280 células fora do "42" alcançáveis, 0 loops e paredes coerentes.
- `a_maze_ing.py config.txt` roda sem erro e agora imprime as células já com as paredes abertas.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/generator.py` | novo: função `generate_perfect` |
| `src/mazegen/__init__.py` | exporta `generate_perfect` |
| `src/main.py` | chama o gerador depois de criar o `Map`, passando o `SEED` do config |
| `tests/test_generator.py` | novo: 9 testes |

`Cell` e `Map` não foram alterados.

## Código

```python
def generate_perfect(maze_map: Map, seed: Optional[int] = None) -> None:
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
```

## Como funciona

O algoritmo é a busca em profundidade com retorno (em inglês, *recursive backtracker* ou *randomized DFS*). A ideia é andar pelo mapa como alguém que cava um túnel:

1. Começa numa célula e a marca como visitada.
2. Olha as quatro vizinhas e separa as que servem: dentro do mapa, fora do "42" e ainda não visitadas.
3. Se alguma serve, sorteia uma, abre a parede até ela e anda para lá.
4. Se nenhuma serve, é um beco: volta uma célula e tenta de novo a partir dela.
5. Termina quando voltou até o início e não sobrou nada para tentar.

### A pilha

`stack` guarda o caminho percorrido desde o início até a célula atual. A célula atual é sempre a última da lista (`stack[-1]`).

- Andar para uma vizinha é `stack.append(neighbour)`.
- Voltar uma célula é `stack.pop()`.

A versão clássica desse algoritmo usa recursão. Usei a pilha explícita porque o Python limita a recursão a cerca de 1000 chamadas, e um labirinto 50x50 pode ter um caminho com mais de 1000 células.

### Por que não há loops

Uma parede só é aberta em direção a uma célula que **nunca foi visitada**. Cada célula, portanto, é alcançada por uma única parede aberta: a que foi usada na primeira vez que o algoritmo chegou nela. Com `N` células ligadas por exatamente `N - 1` aberturas, o resultado é uma árvore, e uma árvore não tem loops.

### Por que tudo fica conectado

O algoritmo só desiste de uma célula quando todas as vizinhas dela já foram visitadas. Então, se uma célula livre tem alguma vizinha visitada, ela também acaba sendo visitada. Como a margem de 1 célula da Task 2 garante que as células livres formam uma região só, todas são alcançadas.

### O "42" e as bordas

- As células com `is_42` são descartadas no passo 2, então o algoritmo nunca entra nelas e nunca abre parede para elas. Ficam com as quatro paredes fechadas. O gerador consulta apenas `cell.is_42`, como a Task 2 pedia.
- As bordas continuam fechadas porque `open_wall` só abre parede entre duas células que existem.

### A seed

`random.Random(seed)` cria um gerador de números aleatórios próprio desta chamada. Com a mesma seed, ele devolve sempre a mesma sequência de sorteios, e portanto o mesmo labirinto. Com `seed=None`, o Python usa o relógio/sistema e cada chamada dá um labirinto diferente.

Usei um gerador próprio, e não o `random.seed()` global, para que nada fora desta função consiga alterar o resultado.

A ordem das vizinhas também precisa ser fixa para a seed funcionar: ela vem do dicionário `DIRECTIONS`, que é sempre percorrido como `N`, `S`, `E`, `W`.

## Decisões que tomei

- **Uma função, não uma classe.** A Task 7 é a que cria a classe `MazeGenerator` juntando tudo. Por enquanto a função recebe o `Map` e o altera.
- **O algoritmo.** Escolhi a busca em profundidade por ser a mais curta de escrever e de explicar. Ela produz corredores longos e poucos becos. O README (Task 13) precisa justificar essa escolha.
- **Ponto de partida: a entrada do mapa.** Se o `Map` não tiver entrada, começa em `(0, 0)`. O ponto de partida não muda o fato de o labirinto ser perfeito, só o desenho.
- **O gerador espera um mapa recém-criado.** Ele não fecha paredes antes de começar. Para gerar outro labirinto, cria-se outro `Map`.
- **O `main.py` usa `config.get("SEED")`.** `SEED` é opcional no config; sem ela, o valor é `None` e cada execução gera um labirinto diferente.

## O que esta task não faz

- Não lê `PERFECT`: o labirinto sai sempre perfeito. O modo não-perfeito é a Task 6.
- Não marca o caminho (`cell.path`): é a Task 4.
- Não escreve o arquivo de saída: é a Task 5.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando três coisas valem:

| Critério | Teste que cobre |
|----------|-----------------|
| Toda célula fora do "42" é alcançável | `test_every_free_cell_is_reachable` |
| As bordas externas continuam fechadas | `test_borders_stay_closed` |
| Duas execuções com a mesma seed dão o mesmo resultado | `test_same_seed_gives_same_maze` |
| Sem nenhum loop (da descrição da task) | `test_has_no_loops` |

Os testes de conectividade, loops e bordas rodam em cinco tamanhos: 15x20 e 7x9 (com o "42"), 5x5 e 1x8 (pequenos demais para o padrão) e 1x1.

`test_has_no_loops` conta as paredes abertas e compara com `células livres - 1`. Junto com o teste de conectividade, isso prova que o labirinto é uma árvore.

Testes além dos critérios:

- `test_42_cells_stay_closed`: as 20 células do "42" continuam com as quatro paredes fechadas.
- `test_neighbours_agree_on_shared_wall`: duas vizinhas sempre concordam sobre a parede entre elas.
- `test_different_seeds_give_different_mazes`: seeds 1 e 2 dão labirintos diferentes.
- `test_works_without_seed_and_without_entry`: funciona com `seed=None` e sem entrada.
- `test_does_not_mark_path_or_change_42`: o gerador não mexe em `path` nem em `is_42`.

## Verificação visual

Mapa 15x20, entrada `(0, 0)`, seed 42. `###` são as células do "42":

```
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |       |       |               |                       |       |           |
+   +   +   +   +   +   +   +---+   +---+   +---+---+---+   +   +   +---+   +   +
|   |   |   |   |   |   |       |       |           |           |       |   |   |
+   +   +   +   +   +   +---+   +---+   +   +---+   +---+---+---+---+   +   +   +
|       |       |   |   |   |   |       |       |       |           |       |   |
+---+---+---+---+   +   +   +   +---+   +---+---+---+   +   +---+---+---+---+   +
|           |       |       |       |                   |                   |   |
+   +---+---+   +---+---+---+---+   +---+---+---+---+---+   +---+---+---+   +   +
|               |                   |                       |           |       |
+   +---+---+---+   +---+---+   +---+   +---+---+---+---+---+---+---+   +---+---+
|   |                   |###|   |###|   |###|###|###|   |           |           |
+   +---+---+   +---+   +---+   +---+   +---+---+---+   +   +   +   +   +---+   +
|           |   |       |###|   |###|           |###|       |   |   |   |   |   |
+---+---+   +   +   +---+---+---+---+   +---+---+---+---+---+   +   +   +   +   +
|       |   |   |   |   |###|###|###|   |###|###|###|           |   |   |       |
+   +   +   +---+   +   +---+---+---+   +---+---+---+   +---+---+   +   +   +---+
|   |   |   |       |           |###|   |###|               |   |   |   |       |
+   +---+   +   +---+   +---+   +---+   +---+---+---+---+   +   +   +   +---+---+
|   |       |   |       |       |###|   |###|###|###|       |       |   |       |
+   +   +---+   +   +---+   +---+---+   +---+---+---+   +---+   +---+   +   +   +
|   |           |   |   |               |               |       |           |   |
+   +---+---+---+   +   +---+---+---+---+---+---+---+   +   +---+---+---+---+   +
|       |       |       |                               |   |               |   |
+   +   +   +   +---+   +---+---+   +---+---+---+---+---+   +   +   +---+   +   +
|   |   |   |       |   |           |               |       |   |   |       |   |
+   +   +   +---+   +   +   +---+---+   +---+---+---+   +---+   +   +---+   +   +
|   |       |   |   |       |       |               |   |       |       |   |   |
+   +---+---+   +   +---+---+   +---+   +---+---+   +   +---+---+---+   +   +   +
|               |                               |                       |       |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
```

Esse desenho e o arquivo hexadecimal passado ao `maze_analyzer.py` foram feitos por um script temporário, fora do projeto. O render de verdade é a Task 8 e o arquivo de saída é a Task 5.

Saída do analisador para esse mesmo labirinto:

```
Maze size        : 20 x 15 (300 cells)
Entry            : (0, 0)   Exit: (19, 14) (reachable)
Reachable region : 280 cells (0 corridor(s) unreachable)
Independent loops: 0 / 224 possible (path ratio 0%)
Dead-ends        : 28 real + 3 enclosed by the '42' (tolerated)
Corners + centre : all reachable
Wall coherence   : OK (all shared walls match)

Verdict: PERFECT maze: a single path, no loop -> matches PERFECT=True
```

## Como rodar

Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- O `config.txt` atual tem `PERFECT=False`, mas o programa gera um labirinto perfeito mesmo assim, porque o modo não-perfeito ainda não existe (Task 6).
- O `main.py` continua com o teu `pprint` de todas as células: num mapa 20x15 são 300 linhas no terminal. Não mexi nisso.
- Os testes das Tasks 1 e 2 que criam mapas pequenos continuam imprimindo a mensagem de "too small" no meio da saída do `unittest`. Os testes novos escondem essa mensagem.
