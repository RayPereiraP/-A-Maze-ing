# Task 2 — Output

Implementação do padrão "42" pedido em [TASK_2.md](TASK_2.md): a propriedade `Cell.is_42` e a etapa final de `Map.__init__` que marca o desenho no centro do labirinto.

## Resultado

- 20 testes, 20 passando (12 da Task 1 + 8 novos).
- `mypy` sem erros com as flags do subject.
- `flake8` sem avisos novos. Continuam os dois avisos que já existiam em `src/main.py` antes desta task (`pprint` importado sem uso e `project_map` atribuído sem uso); não mexi neles porque são do teu código em andamento.
- `a_maze_ing.py config.txt` roda sem erro e, com o `config.txt` atual (20x15), o "42" é marcado.

## Arquivos alterados

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/cell.py` | novo atributo `is_42` |
| `src/mazegen/map.py` | constantes `PATTERN_42` e `PATTERN_42_MARGIN`, parâmetros `entry`/`exit` e o método `_mark_42` |
| `src/main.py` | passa a entrada e a saída do config para o `Map` |
| `tests/test_map.py` | import corrigido, 2 testes da Task 1 ajustados, 8 testes novos |

## O que foi feito

### `Cell.is_42`

Uma linha a mais no construtor, no mesmo formato dos outros atributos:

```python
self.is_42: bool = False
```

### O desenho, definido em um único lugar

No topo de `src/mazegen/map.py`:

```python
PATTERN_42: Tuple[str, ...] = (
    "#.#.###",
    "#.#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)
PATTERN_42_MARGIN: int = 1
```

`#` é uma célula do "42" e `.` é uma célula normal. O desenho tem 5 linhas por 7 colunas e 20 células marcadas: o "4" ocupa as 3 primeiras colunas, o "2" as 3 últimas, e a coluna do meio separa os dois.

A altura e a largura não estão escritas em nenhum outro lugar: o código lê `len(PATTERN_42)` e `len(PATTERN_42[0])`. Para trocar o desenho, basta editar essas linhas.

### `Map.__init__`

O construtor ganhou dois parâmetros opcionais, `entry` e `exit`, cada um no formato `(row, col)`. As etapas que já existiam continuam iguais e na mesma ordem; no final entraram três linhas:

```python
self.entry: Optional[Position] = entry
self.exit: Optional[Position] = exit
self._mark_42()
```

### `Map._mark_42`, passo a passo

1. Calcula a altura e a largura do desenho a partir de `PATTERN_42`.
2. **Checagem 1 — tamanho.** Se o mapa tiver menos que `altura + 2 * margem` linhas ou `largura + 2 * margem` colunas, imprime o erro e sai.
3. Calcula o canto superior esquerdo do desenho: `top = (rows - altura) // 2` e `left = (cols - largura) // 2`.
4. Monta a lista `positions` com as posições `(row, col)` de todos os `#`, já deslocadas por `top` e `left`.
5. **Checagem 2 — entrada/saída.** Se `entry` ou `exit` estiver nessa lista, imprime o erro e sai.
6. Só então percorre a lista e põe `is_42 = True` em cada célula.

As duas checagens acontecem antes de qualquer escrita, então o desenho nunca fica pela metade.

As mensagens vão para o `stderr`, como as outras mensagens de erro do projeto, e o programa continua normalmente:

```
Error: the maze is too small for the "42" pattern; pattern omitted.
Error: the entry or the exit is on the "42" pattern; pattern omitted.
```

### `src/main.py`

O config usa `(x, y)` e o `Map` usa `(row, col)`, então a conversão é feita ali: `ENTRY=3,0` vira `entry=(0, 3)`. Era o ponto de atenção anotado no final da Task 1.

## Decisões que tomei

- **Tamanho do desenho: 5x7.** É o menor "42" que continua legível, com cada dígito em 3 colunas.
- **Margem de 1 célula: o mapa mínimo é 7 linhas por 9 colunas.** Sem a margem, um mapa 5x7 seria ocupado inteiro pelo desenho, e as células normais ficariam separadas em pedaços que o gerador da Task 3 não conseguiria ligar. Com 1 célula livre em volta, todas as células normais continuam alcançáveis.
- **Quando a sobra é ímpar, o desenho fica 1 célula para cima ou para a esquerda.** É o efeito do `//`. Num mapa 20x15 o desenho começa na linha 5 e na coluna 6.
- **`entry` e `exit` são opcionais.** A task diz que a entrada e a saída precisam ser comparadas com o desenho, mas o `Map` não as conhecia. Deixei opcionais para que `Map(3, 5)` continue funcionando como na Task 1. Se nenhuma for informada, só a checagem de tamanho é feita.
- **Só as células `#` contam como sobreposição.** Uma entrada dentro da área 5x7 mas em cima de um `.` não cancela o desenho, porque aquela célula não faz parte do "42".
- **`_mark_42` é um método separado, chamado só pelo `__init__`.** A marcação continua acontecendo dentro da construção; o método existe para o `__init__` não ficar comprido.

## O que esta task não faz

A task pede só a marcação. Fechar as células do "42" e impedir o gerador de entrar nelas é assunto da Task 3, que deve consultar apenas `cell.is_42`. Hoje nenhum outro código do projeto precisa saber quem é do "42", então não existe mecanismo paralelo.

## Ajustes nos testes da Task 1

- **Import.** `tests/test_map.py` importava `from mazegen import ...`, mas o pacote foi movido para `src/mazegen` no último commit, e por isso os 12 testes não rodavam mais. Troquei para `from src.mazegen import ...`.
- `test_initial_state` agora também confere `is_42 == False`.
- `test_does_not_know_position` passou a esperar o atributo `is_42` na lista.

## Critérios de aceitação

| Critério | Teste que cobre |
|----------|-----------------|
| `Cell` tem `is_42`, padrão `False` | `test_initial_state` |
| Mapa grande, sem sobreposição: só as células do "42" têm `is_42 == True` | `test_marks_centred_pattern` |
| Mapa pequeno demais: nenhuma célula marcada, mensagem no console | `test_too_small_omits_pattern` |
| Entrada ou saída sobre o desenho: nenhuma célula marcada, mensagem no console | `test_entry_on_pattern_omits_pattern`, `test_exit_on_pattern_omits_pattern` |
| Construção do labirinto inalterada fora do padrão | os 12 testes da Task 1 e `test_pattern_does_not_touch_walls_or_path` |

`test_marks_centred_pattern` compara o conjunto de posições marcadas com um desenho 9x11 escrito à mão no teste. Isso prova as duas metades do critério: as células certas estão marcadas e nenhuma outra está.

Testes além dos critérios:

- `test_marks_without_entry_and_exit`: o desenho é marcado mesmo sem entrada e saída.
- `test_smallest_map_that_fits`: um mapa 7x9 recebe as 20 células.
- `test_entry_in_gap_of_pattern_keeps_pattern`: entrada num `.` dentro da área do desenho não cancela o padrão.

## Verificação visual

Mapa 15x20 com entrada em `(0, 0)` e saída em `(14, 19)`, o mesmo do `config.txt`:

```
....................
....................
....................
....................
....................
......#.#.###.......
......#.#...#.......
......###.###.......
........#.#.........
........#.###.......
....................
....................
....................
....................
....................
```

## Como rodar

Na raiz do projeto, com o mesmo Python da Task 1:

```powershell
.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Ponto de atenção

Os testes da Task 1 criam mapas pequenos, como `Map(3, 3)`, e cada um agora imprime a mensagem de "too small" no `stderr`. Os testes passam, mas a saída do `unittest` fica com essas linhas no meio. Os testes novos capturam a mensagem com `build_map`, então não fazem esse barulho.
