# Task 7 — Output

Implementação da Task 7 do [TASKS.md](TASKS.md): a classe `MazeGenerator`, que junta as Tasks 1 a 6 num único ponto de entrada. Não havia um `TASK_7.md`, então segui o `TASKS.md` e o capítulo VI do subject (Code reusability requirements).

## Resultado

- 68 testes, 68 passando (57 das Tasks 1 a 6 + 11 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- O `main.py` passou a usar a classe, e os arquivos de saída ficaram **idênticos, byte a byte**, aos da Task 6 nos três configs que comparei (20x15 perfeito, 20x15 não-perfeito e 5x7 não-perfeito).
- O critério "Pronta quando" é cumprido com 3 linhas (ver abaixo).

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/maze_generator.py` | novo: classe `MazeGenerator` |
| `src/mazegen/__init__.py` | exporta `MazeGenerator` |
| `src/main.py` | usa a classe no lugar das quatro chamadas soltas |
| `tests/test_maze_generator.py` | novo: 11 testes |

`Cell`, `Map`, o gerador, o solver e o writer não foram alterados.

## Como usar

Esta é a documentação curta que o subject pede (instanciar, passar parâmetros, acessar a estrutura e uma solução). Ela vai precisar ser copiada para o README na Task 13.

### Exemplo básico

```python
from src.mazegen import MazeGenerator

generator = MazeGenerator(15, 20, entry=(0, 0), exit=(14, 19), seed=42)
print(generator.path)
```

Saída:

```
EESSSWWSSSENEESSSENESEESWSEEEEEEENENESSEEENESSSSS
```

O labirinto é gerado na criação do objeto. Não é preciso chamar mais nada.

### Parâmetros

| Parâmetro | Tipo | Padrão | Significado |
|-----------|------|--------|-------------|
| `rows` | `int` | obrigatório | número de linhas (o `HEIGHT` do config) |
| `cols` | `int` | obrigatório | número de colunas (o `WIDTH` do config) |
| `entry` | `(row, col)` | obrigatório | célula de entrada |
| `exit` | `(row, col)` | obrigatório | célula de saída |
| `perfect` | `bool` | `False` | `True`: um único caminho, sem loops. `False`: tabuleiro com loops |
| `seed` | `int` ou `None` | `None` | a mesma seed gera sempre o mesmo labirinto; `None` gera um diferente a cada vez |

Toda posição é `(row, col)`, com `(0, 0)` no canto superior esquerdo. É a mesma convenção do `Map`.

Parâmetros inválidos levantam `ValueError`: dimensão menor que 1, entrada ou saída fora do labirinto, ou entrada igual à saída.

### Acessar a estrutura

`generator.maze_map` é o `Map` das Tasks 1 e 2:

```python
maze_map = generator.maze_map
cell = maze_map.cell(0, 0)      # a célula da linha 0, coluna 0
print(cell.N, cell.S, cell.E, cell.W)   # True = parede fechada
print(cell.is_42)               # True se a célula desenha o "42"
print(cell.path)                # True se a célula está no caminho mais curto

for row in maze_map.grid:       # ou percorrer tudo
    for cell in row:
        ...
```

### Acessar a solução

`generator.path` é o caminho mais curto da entrada até a saída, como uma string de letras `N`, `S`, `E`, `W`. As células desse caminho também ficam com `cell.path == True`.

### Gerar outro labirinto

```python
generator.seed = 7
generator.generate()
```

`generate()` monta um `Map` novo e recalcula o caminho. Com a mesma seed o resultado é o mesmo labirinto, então é preciso trocar a seed (ou usar `None`) para obter outro.

### Gravar o arquivo de saída

```python
generator.write("maze.txt")
```

Grava no formato do subject (Task 5). Levanta `OSError` se o arquivo não puder ser escrito.

## Código

```python
class MazeGenerator:

    def __init__(
        self,
        rows: int,
        cols: int,
        entry: Position,
        exit: Position,
        perfect: bool = False,
        seed: Optional[int] = None,
    ) -> None:
        if rows < 1 or cols < 1:
            raise ValueError("The maze needs at least 1 row and 1 column.")
        for name, (row, col) in (("entry", entry), ("exit", exit)):
            if not (0 <= row < rows and 0 <= col < cols):
                raise ValueError(f"The {name} must be inside the maze.")
        if entry == exit:
            raise ValueError("The entry and the exit must be different.")
        self.rows: int = rows
        self.cols: int = cols
        self.entry: Position = entry
        self.exit: Position = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.maze_map: Map
        self.path: str
        self.generate()

    def generate(self) -> None:
        maze_map = Map(self.rows, self.cols, self.entry, self.exit)
        generate_perfect(maze_map, self.seed)
        if not self.perfect:
            open_loops(maze_map, self.seed)
        self.path = shortest_path(maze_map)
        self.maze_map = maze_map

    def write(self, filename: Union[str, Path]) -> None:
        write_maze(self.maze_map, self.path, filename)
```

## Como funciona

A classe não tem algoritmo próprio. Ela guarda os parâmetros e chama, na ordem certa, o que as tasks anteriores já fazem:

| Passo em `generate()` | Task |
|-----------------------|------|
| `Map(...)`: cria a grade e marca o "42" | 1 e 2 |
| `generate_perfect(...)`: abre as paredes do labirinto perfeito | 3 |
| `open_loops(...)`: só se `perfect` for falso | 6 |
| `shortest_path(...)`: calcula o caminho e marca `cell.path` | 4 |

E `write()` chama o `write_maze` da Task 5.

A ordem importa em dois pontos: o caminho é calculado depois de `open_loops`, porque as paredes extras criam atalhos; e o `Map` é sempre novo, porque `generate_perfect` espera todas as paredes fechadas.

As linhas `self.maze_map: Map` e `self.path: str` no `__init__` só declaram os tipos dos dois atributos. Quem dá valor a eles é o `generate()`, chamado logo em seguida.

## Decisões que tomei

- **A classe é uma fachada sobre as funções das Tasks 3 a 6.** As funções continuam existindo e testadas; a classe só as organiza. A alternativa seria mover o código delas para dentro da classe, como métodos. Não fiz isso porque reescreveria quatro arquivos e os testes deles sem mudar o comportamento. O subject pede "a geração como uma classe única": quem usa o módulo só precisa da `MazeGenerator`, mas se o avaliador exigir que o algoritmo esteja dentro da classe, essa mudança terá de ser feita.
- **O labirinto é gerado no `__init__`.** Assim `maze_map` e `path` existem sempre, e nunca é preciso testar se o labirinto "já foi gerado". Também é o que deixa o exemplo com 3 linhas.
- **Posições em `(row, col)`, tamanho em `rows, cols`.** Todo o `mazegen` usa essa convenção desde a Task 1. O config usa `(x, y)` e `WIDTH, HEIGHT`; a troca continua sendo feita num lugar só, no `main.py`.
- **`perfect` tem padrão `False`.** O subject diz que o modo não-perfeito é o padrão.
- **A classe valida os parâmetros.** O parser já valida o config, mas a classe não pode depender dele: quem importar o `mazegen` em outro projeto não passa pelo parser.
- **`entry` e `exit` são obrigatórios aqui**, embora sejam opcionais no `Map`. Sem eles não há caminho para calcular.
- **`write()` faz parte da classe.** O `TASKS.md` diz que ela junta as Tasks 1 a 6, e a Task 5 é o arquivo de saída.
- **Arquivo `maze_generator.py`, separado do `generator.py`.** O `generator.py` guarda os dois algoritmos; a classe fica no próprio arquivo.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "um script de 5 linhas importa a classe, gera um labirinto e lê o caminho".

| Critério | Teste que cobre |
|----------|-----------------|
| Um script curto importa a classe, gera e lê o caminho | `test_five_line_script` |
| Recebe tamanho, entrada, saída, perfect e seed | `test_stores_the_parameters` |
| Dá acesso à estrutura | `test_gives_access_to_the_structure` |
| Dá acesso ao caminho | `test_path_leads_from_entry_to_exit` |
| Não depende do parser nem do terminal | `test_does_not_load_the_parser` |

`test_five_line_script` roda o script de 3 linhas num processo Python separado, como um usuário faria, e compara o que ele imprime com o caminho esperado.

`test_does_not_load_the_parser` importa `src.mazegen` num processo separado e confere que `src.parser` e `src.main` não foram carregados junto.

Testes além dos critérios:

- `test_perfect_mode_has_no_loops` e `test_default_mode_has_loops`: os dois modos, e o padrão `perfect=False`.
- `test_same_seed_gives_same_maze`: mesma seed, mesmo labirinto e mesmo caminho.
- `test_generate_builds_a_new_maze`: `generate()` cria outro `Map`; com a mesma seed é igual, com outra seed é diferente.
- `test_write_creates_the_output_file`: o arquivo gravado tem o conteúdo esperado.
- `test_invalid_parameters`: os seis casos de `ValueError`.

## Como rodar

Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- **O import é `from src.mazegen import ...`, não `from mazegen import ...`.** Todos os arquivos do pacote importam uns aos outros com o prefixo `src.` (por exemplo `from src.mazegen.map import Map`). Isso funciona a partir da raiz do projeto, mas não funcionará quando o pacote for instalado com `pip` com o nome `mazegen` (Task 11). Lá os imports internos terão de virar relativos (`from .map import Map`) ou perder o prefixo. Não mexi nisso agora porque é a estrutura que escolheste ao mover a pasta, e a mudança afeta todos os arquivos e testes.
- **Regerar no menu (Task 9).** Com `SEED` fixa no config, `generate()` devolve sempre o mesmo labirinto. A opção "gerar outro labirinto" do menu vai precisar trocar `generator.seed` antes de chamar `generate()`.
- **Mensagem do "42" a cada geração.** Num labirinto pequeno demais, cada `generate()` imprime de novo o aviso de padrão omitido, porque ele vem do `Map.__init__`.
- **Limpeza.** Removi a pasta `__pycache__/` que estava na raiz. Ela continha só `maze_analyzer.cpython-310.pyc` e tinha sido criada pelo meu script de varredura da Task 6.
- **O `pprint` do `main.py`** continua imprimindo todas as células; só troquei `project_map.grid` por `generator.maze_map.grid`.
