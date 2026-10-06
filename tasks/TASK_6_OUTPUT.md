# Task 6 — Output

Implementação da Task 6 do [TASKS.md](TASKS.md): o modo não-perfeito (`PERFECT=False`), que parte do labirinto perfeito e abre paredes extras até virar um tabuleiro tipo Pac-Man. Não havia um `TASK_6.md`, então segui o `TASKS.md` e a seção IV.4 do subject.

## Resultado

- 57 testes, 57 passando (47 das Tasks 1 a 5 + 10 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- O `maze_analyzer.py` do subject classificou como `Pac-Man-USABLE` todos os 2200 tabuleiros de uma varredura: 11 tamanhos (de 3x3 a 50x50) com 200 seeds cada.
- Com `PERFECT=True` nada mudou: o analisador continua respondendo `PERFECT maze`.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/generator.py` | nova função `open_loops`, três funções auxiliares e as constantes `MIN_LOOPS` e `OPEN_AREA_SIZE` |
| `src/mazegen/__init__.py` | exporta `open_loops` |
| `src/main.py` | chama `open_loops` quando `PERFECT` é falso, antes de calcular o caminho |
| `tests/test_loops.py` | novo: 10 testes |

`generate_perfect`, `Cell`, `Map`, o solver e o writer não foram alterados.

## As regras do subject e onde cada uma é atendida

| Regra do modo não-perfeito | Como é atendida |
|----------------------------|-----------------|
| Todo corredor é alcançável | o labirinto perfeito já é conexo, e abrir parede nunca desconecta |
| Os quatro cantos são corredores | a margem de 1 célula da Task 2 garante que nenhum canto é do "42" |
| O centro é corredor | a coluna do meio do desenho do "42" é o espaço entre o "4" e o "2" |
| Pelo menos 2 rotas independentes (loops) | `open_loops` abre paredes até ter `MIN_LOOPS` loops |
| Dead-ends raros | `open_loops` abre uma parede de cada dead-end |
| Nenhuma área aberta 3x3 | `open_loops` recusa a parede que completaria uma |

As três primeiras não precisaram de código novo: já eram consequência das Tasks 2 e 3. As três últimas são o trabalho desta task.

## Código

```python
MIN_LOOPS: int = 2
OPEN_AREA_SIZE: int = 3


def open_loops(maze_map: Map, seed: Optional[int] = None) -> None:
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
```

## Como funciona

A função tem duas partes: juntar as paredes candidatas e decidir, uma por uma, se abre.

### Parte 1: as candidatas

Uma candidata é uma parede **fechada** entre **duas células normais**. Ficam de fora:

- as bordas, porque a vizinha não existe;
- qualquer parede de uma célula do "42", para o desenho continuar fechado.

O laço olha só as direções `S` e `E` de cada célula. A parede norte de uma célula é a parede sul da célula de cima, então olhar as quatro direções listaria cada parede duas vezes.

Depois a lista é embaralhada com a seed, para as paredes abertas não ficarem concentradas no canto de cima do mapa.

### Parte 2: abrir ou não

Para cada candidata, a parede é **desejada** se uma destas coisas for verdade:

- o labirinto ainda tem menos de `MIN_LOOPS` loops; ou
- uma das duas células é um dead-end (tem exatamente uma parede aberta).

E ela só é aberta se, além de desejada, **não completar uma área aberta 3x3**.

### Por que cada parede aberta é um loop

No labirinto perfeito já existe um caminho entre quaisquer duas células. Abrir uma parede entre duas vizinhas cria um segundo caminho entre elas: os dois juntos formam um loop. Por isso `loops += 1` a cada abertura conta certo, sem precisar procurar os loops.

### Por que uma passada só resolve os dead-ends

Um dead-end tem uma parede aberta e até três fechadas, e todas as fechadas que podem ser abertas estão na lista. Quando o laço chega na primeira delas, a célula ainda é um dead-end, então a parede é aberta e a célula deixa de ser. As outras paredes dela, mais adiante na lista, já não são desejadas por causa dela.

Abrir parede nunca cria um dead-end novo, só remove. Por isso não é preciso repetir a passada.

### A regra do 3x3

Uma área aberta é um quadrado de 3x3 células sem nenhuma parede interna. Um quadrado desses tem 12 paredes internas: 6 entre células lado a lado e 6 entre células uma em cima da outra.

`_completes_open_area` responde, **antes** de abrir, se a parede completaria um quadrado assim:

1. Lista todos os quadrados 3x3 que contêm as duas células da parede.
2. Para cada um, conta as paredes internas abertas (`_open_inner_walls`).
3. Se algum tem 11 das 12 abertas, a que falta é justamente a candidata, que ainda está fechada. Abrir completaria a área, então a resposta é "sim" e a parede é recusada.

Conferir antes de abrir evita ter de fechar a parede de volta, coisa que o `Map` não sabe fazer.

Áreas de 2x2, 2x3 e 3x2 continuam permitidas, como o subject diz.

## Decisões que tomei

- **Função separada, chamada depois de `generate_perfect`.** O `TASKS.md` descreve o modo como "parte do labirinto perfeito e abre paredes extras". O modo perfeito fica intocado, e o `main.py` decide se chama a segunda função.
- **`MIN_LOOPS = 2`.** É o mínimo do subject: um labirinto perfeito com só uma parede removida não é aceito.
- **A mesma seed é usada nas duas funções.** `open_loops` cria o próprio `random.Random(seed)`. Assim, mesma seed e mesmo `PERFECT` dão sempre o mesmo arquivo.
- **Nenhuma parede é fechada.** O tabuleiro é o labirinto perfeito mais algumas aberturas. O teste `test_only_opens_walls` confere isso.
- **O caminho é calculado depois.** No `main.py`, `shortest_path` vem depois de `open_loops`, porque as paredes novas criam atalhos. No exemplo abaixo o caminho cai de 164 para 49 passos.

## Ponto que precisa da tua decisão: dead-ends e o bônus

Tu pediste só a parte mandatória, sem o bônus de "zero dead-ends". Esta task encosta nele, e quero deixar claro o que acontece:

- A regra mandatória é "dead-ends raros, alguns tolerados". O analisador tolera no máximo 2.
- Um labirinto perfeito 20x15 tem cerca de 28 dead-ends. Para chegar a 2 ou menos, é preciso remover quase todos.
- O jeito mais simples de fazer isso é tentar abrir uma parede de **cada** dead-end. Não escrevi nenhum código para garantir zero, mas o resultado costuma ser zero.

Na varredura de 2200 tabuleiros, 2170 saíram com 0 dead-ends reais e 30 com 1. Nesses 30, a única parede disponível completaria uma área 3x3 e foi recusada.

Quando sai zero, o analisador escreve `bonus-grade (perfectly braided)`. Não é um recurso a mais: é efeito colateral de cumprir a regra mandatória. Se preferires deixar alguns dead-ends de propósito, dá para trocar a condição do dead-end por um sorteio, mas aí o limite de 2 deixa de ser garantido.

Os dead-ends cercados pelo "42" (3 no mapa 20x15) continuam existindo: todas as paredes fechadas deles dão para o "42" ou para a borda. O analisador os conta à parte e os tolera.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando o `maze_analyzer.py` reporta o arquivo como tabuleiro jogável.

| Critério | Como foi verificado |
|----------|---------------------|
| O analisador reporta tabuleiro jogável | varredura de 2200 tabuleiros + execução do programa em 20x15 e 5x7 |
| Pelo menos 2 loops | `test_has_at_least_two_loops` |
| Poucos dead-ends | `test_dead_ends_are_rare` |
| Nenhuma área aberta 3x3 | `test_has_no_open_area`, `test_refuses_the_wall_that_completes_an_open_area` |
| Cantos e centro são corredores | `test_every_free_cell_is_still_reachable`, `test_centre_is_a_free_cell` |

Os três primeiros testes rodam em 5 tamanhos de mapa com 10 seeds cada (50 tabuleiros).

O analisador **não** confere a regra do 3x3. Ela é coberta só pelos meus testes:

- `test_has_no_open_area` procura quadrados 3x3 totalmente abertos nos 50 tabuleiros.
- `test_refuses_the_wall_that_completes_an_open_area` monta à mão o pior caso: um mapa 3x3 em que o centro está ligado aos quatro lados e cada canto é um dead-end. Faltam 4 paredes para a área ficar toda aberta. A função abre 3 e recusa a última, qualquer que seja a seed.

Testes além dos critérios:

- `test_42_and_borders_stay_closed`: o "42" e as bordas continuam fechados.
- `test_only_opens_walls`: toda parede aberta no labirinto perfeito continua aberta.
- `test_same_seed_gives_same_board`: a mesma seed dá o mesmo tabuleiro.
- `test_path_is_valid_and_not_longer`: o caminho continua válido e nunca fica mais longo que o do labirinto perfeito.

A varredura com o analisador foi manual, por um script temporário fora do projeto. Os testes automáticos não chamam o analisador.

## Verificação visual

Mapa 15x20, entrada `0,0`, saída `19,14`, seed 42, `PERFECT=False`. `o` é o caminho mais curto e `###` é o "42". É o mesmo labirinto da Task 3, com 30 paredes a mais abertas:

```
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| o   o   o |       |                                       |                   |
+   +   +   +   +   +   +   +---+   +---+   +---+---+---+   +   +   +---+   +   +
|   |   | o |   |   |   |       |       |           |           |       |   |   |
+   +   +   +   +   +   +---+   +---+   +   +---+   +   +---+---+---+   +   +   +
|       | o         |       |   |       |               |           |       |   |
+---+---+   +---+   +   +   +   +   +   +---+---+---+   +   +---+   +---+---+   +
| o   o   o |       |       |       |                   |                   |   |
+   +---+---+   +---+---+---+---+   +---+---+---+---+---+   +---+---+---+   +   +
| o             |                   |                                   |       |
+   +---+---+---+   +---+---+   +---+   +---+---+---+   +---+---+---+   +---+---+
| o | o   o   o         |###|   |###|   |###|###|###|   |           |           |
+   +   +---+   +---+   +---+   +---+   +---+---+---+   +   +   +   +   +---+   +
| o   o     | o |       |###|   |###|           |###|       |   |   |   |       |
+---+---+   +   +   +---+---+---+---+   +---+---+---+---+---+   +   +   +   +   +
|       |   | o | o   o |###|###|###|   |###|###|###|           |   |   |       |
+   +   +   +   +   +   +---+---+---+   +---+---+---+   +---+---+   +   +   +---+
|   |   |   | o   o | o   o   o |###|   |###|             o   o |   |   |       |
+   +   +   +   +---+   +---+   +---+   +---+---+---+---+   +   +   +   +---+   +
|   |       |   |       | o   o |###|   |###|###|###| o   o | o     |   | o   o |
+   +   +---+   +   +---+   +---+---+   +---+---+---+   +---+   +---+   +   +   +
|   |                   | o   o   o   o   o   o   o   o |     o   o   o   o | o |
+   +---+---+---+   +   +---+---+---+---+---+---+---+   +   +---+---+---+---+   +
|       |       |       |                               |   |               | o |
+   +   +   +   +---+   +   +---+   +---+---+---+---+---+   +   +   +---+   +   +
|   |   |   |       |   |           |                       |   |   |       | o |
+   +   +   +   +   +   +   +---+---+   +---+---+---+   +   +   +   +   +   +   +
|   |       |   |   |       |                       |   |       |       |   | o |
+   +---+---+   +   +---+---+   +---+   +---+---+   +   +---+---+---+   +   +   +
|               |                                                       |     o |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
```

Saída do analisador para o arquivo desse tabuleiro, gerado pelo programa:

```
Maze size        : 20 x 15 (300 cells)
Entry            : (0, 0)   Exit: (19, 14) (reachable)
Reachable region : 280 cells (0 corridor(s) unreachable)
Independent loops: 30 / 224 possible (path ratio 13%)
Dead-ends        : 0 real + 3 enclosed by the '42' (tolerated)
Corners + centre : all reachable
Wall coherence   : OK (all shared walls match)

Verdict: Pac-Man-USABLE: fully connected, corners and centre reachable, 30 independent routes; no real dead-end -> bonus-grade (perfectly braided).
```

## Como rodar

Na raiz do projeto, com `PERFECT=False` no `config.txt`:

```powershell
.\tmp\parser-runtime\python.exe a_maze_ing.py config.txt
.\tmp\parser-runtime\python.exe maze_analyzer.py maze.txt

.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- **Mapas minúsculos não têm como cumprir as regras.** Um mapa 2x2 só tem uma parede a mais para abrir, então fica com 1 loop. Um corredor 1xN não tem nenhuma. A função abre o que der e não dá erro. A partir de 3x3 a varredura passou em todos os casos.
- **O centro quando o "42" é omitido.** Se a entrada ou a saída cair sobre o desenho, o "42" não é marcado e o centro vira uma célula comum, então a regra continua valendo.
- **`tests/test_loops.py` importa funções auxiliares** de `tests/test_generator.py` e `tests/test_solver.py`, para não repetir código. Se esses arquivos forem renomeados, os imports precisam acompanhar.
- **O `maze.txt` da raiz** foi criado por uma execução tua e continua fora do `.gitignore`. Nas minhas verificações gravei numa pasta temporária e não mexi nele.
