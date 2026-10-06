# Task 5 — Output

Implementação da Task 5 do [TASKS.md](TASKS.md): o arquivo de saída, no formato da seção IV.5 do subject. Não havia um `TASK_5.md`, então segui a descrição e o "Pronta quando" do `TASKS.md`.

## Resultado

- 47 testes, 47 passando (38 das Tasks 1 a 4 + 9 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- O `maze_analyzer.py` do subject aceitou os arquivos gerados pelo programa (20x15 com seed 42 e 5x7 com seed 2) e respondeu, nos dois: `PERFECT maze: a single path, no loop`, com paredes coerentes e saída alcançável.
- `a_maze_ing.py config.txt` agora cria o arquivo indicado em `OUTPUT_FILE`.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/writer.py` | novo: `WALL_BITS`, `cell_digit`, `maze_to_text` e `write_maze` |
| `src/mazegen/__init__.py` | exporta `write_maze` |
| `src/main.py` | chama `write_maze` com o `OUTPUT_FILE` do config e trata erro de escrita |
| `tests/test_writer.py` | novo: 9 testes |

`Cell`, `Map`, o gerador e o solver não foram alterados.

## O formato

Exemplo real, gerado pelo programa com mapa 5x7, entrada `0,0`, saída `4,6` e seed 2:

```
B9393
AEC2A
A93EA
C6A96
B9683
86D6A
C5556

0,0
4,6
SSSENESSWSWSEEEE
```

- Uma linha por fileira do mapa, um dígito hexadecimal por célula.
- Uma linha vazia.
- A entrada, a saída e o caminho mais curto, uma linha cada.
- Toda linha termina com `\n`, inclusive a última.

## Código

```python
WALL_BITS: Dict[str, int] = {"N": 1, "E": 2, "S": 4, "W": 8}


def cell_digit(cell: Cell) -> str:
    value = 0
    for wall, bit in WALL_BITS.items():
        if getattr(cell, wall):
            value += bit
    return format(value, "X")


def maze_to_text(maze_map: Map, path: str) -> str:
    if maze_map.entry is None or maze_map.exit is None:
        raise ValueError("The map needs an entry and an exit.")
    entry_row, entry_col = maze_map.entry
    exit_row, exit_col = maze_map.exit
    lines: List[str] = [
        "".join(cell_digit(cell) for cell in row) for row in maze_map.grid
    ]
    lines.append("")
    lines.append(f"{entry_col},{entry_row}")
    lines.append(f"{exit_col},{exit_row}")
    lines.append(path)
    return "".join(line + "\n" for line in lines)


def write_maze(maze_map: Map, path: str, filename: Union[str, Path]) -> None:
    text = maze_to_text(maze_map, path)
    # newline="\n" stops Windows from turning each "\n" into "\r\n".
    with open(filename, "w", encoding="utf-8", newline="\n") as file:
        file.write(text)
```

## Como funciona

### O dígito de uma célula

Um dígito hexadecimal vale de 0 a 15, que são exatamente 4 bits: um para cada parede. O subject define qual bit é de qual parede, e a tabela `WALL_BITS` guarda o valor de cada bit:

| Parede | Bit | Valor |
|--------|-----|-------|
| `N` | 0 | 1 |
| `E` | 1 | 2 |
| `S` | 2 | 4 |
| `W` | 3 | 8 |

`cell_digit` soma o valor de cada parede **fechada**. Exemplo com a primeira célula do arquivo acima, `B`:

- `N` fechada: +1
- `E` fechada: +2
- `S` aberta: +0
- `W` fechada: +8

Total 11, que em hexadecimal é `B`. É a entrada `(0, 0)`: canto superior esquerdo, com a única abertura para o sul. O caminho começa com `S`, como esperado.

Uma célula toda fechada é `F` (1 + 2 + 4 + 8 = 15): é assim que as células do "42" aparecem no arquivo.

`format(value, "X")` converte o número para hexadecimal em maiúscula.

### O arquivo inteiro

`maze_to_text` monta uma lista de linhas e só no final junta tudo, pondo `\n` depois de **cada** linha. Assim a regra "toda linha termina com `\n`" vale por construção, sem caso especial para a última.

A linha vazia é a string `""` na lista: com o `\n` dela, vira a linha em branco que separa a grade do rodapé.

### Entrada e saída: `(row, col)` vira `x,y`

Era o ponto de atenção anotado desde a Task 1. O `Map` guarda `(row, col)` e o subject quer `x,y`, onde `x` é a coluna e `y` é a linha. Por isso a coluna é escrita primeiro: `f"{entry_col},{entry_row}"`. É a conversão inversa da que o `main.py` faz ao ler o config.

### `newline="\n"`

No Windows, o Python troca cada `\n` por `\r\n` ao escrever um arquivo de texto. Passar `newline="\n"` ao `open` desliga essa troca, e o arquivo sai igual em qualquer sistema.

## Decisões que tomei

- **Três funções pequenas em vez de uma.** `cell_digit` cuida de uma célula, `maze_to_text` do conteúdo e `write_maze` do disco. Separar o texto da escrita deixa testar o formato sem criar arquivo, e a Task 8 (render) pode reaproveitar a ideia.
- **O caminho é recebido como parâmetro.** `write_maze` não chama `shortest_path`: quem chama decide quando calcular. Na Task 6 o caminho terá de ser calculado depois das paredes extras.
- **Dígitos em maiúscula.** O subject usa `A` no exemplo dele, e o analisador aceita as duas formas.
- **Arquivo existente é substituído.** O subject pede para gerar o arquivo de novo a cada execução.
- **Sem entrada ou sem saída: `ValueError`.** Mesmo comportamento da Task 4.
- **Erro de escrita tratado no `main.py`.** Se o `OUTPUT_FILE` apontar para uma pasta que não existe ou sem permissão, o programa imprime `Error: cannot write the output file: ...` e sai com código 1, sem traceback. Testei com uma pasta inexistente.
- **O módulo fica em `mazegen`.** Assim quem instalar o pacote (Task 11) consegue gravar o labirinto sem depender do `main.py`.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando o `maze_analyzer.py` aceita o arquivo e reporta um labirinto perfeito e coerente.

| Critério | Como foi verificado |
|----------|---------------------|
| O analisador aceita o arquivo e reporta labirinto perfeito e coerente | rodando o programa e depois o analisador, em 20x15 e 5x7 |
| Bit 0 = N, 1 = E, 2 = S, 3 = W; 1 = parede fechada | `test_one_bit_for_each_wall`, `test_examples_of_the_subject` |
| Uma linha por fileira | `test_layout_of_a_generated_maze` |
| Linha vazia, depois entrada, saída e caminho | `test_small_map_written_by_hand`, `test_layout_of_a_generated_maze` |
| Toda linha termina com `\n` | `test_file_has_the_same_text_and_unix_newlines` |

A verificação com o analisador foi manual, pela linha de comando. Os testes automáticos não o chamam.

`test_examples_of_the_subject` usa os dois exemplos escritos no subject: `3` é uma célula aberta para o sul e o oeste, e `A` é uma com leste e oeste fechadas.

`test_small_map_written_by_hand` monta um mapa 2x3 com um corredor e compara o texto inteiro com o esperado, calculado à mão:

```
D53
FFE

0,0
2,1
EES
```

Testes além dos critérios:

- `test_all_closed_and_all_open`: `F` e `0`.
- `test_entry_and_exit_are_written_as_x_y`: a entrada `(row 0, col 3)` é escrita como `3,0`.
- `test_existing_file_is_replaced`: um arquivo antigo e maior não deixa sobras.
- `test_missing_entry_or_exit`: o `ValueError`.

## Saída do analisador

Para o arquivo 20x15 gerado pelo programa com seed 42:

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

O analisador confere a grade, a entrada e a saída. Ele não confere a linha do caminho; essa parte é coberta pelos testes da Task 4.

## Como rodar

Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe a_maze_ing.py config.txt
.\tmp\parser-runtime\python.exe maze_analyzer.py maze.txt

.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- **`maze.txt` no git.** Rodar o programa com o `config.txt` atual cria `maze.txt` na raiz, e o `.gitignore` não o ignora. Nas minhas verificações gravei os arquivos numa pasta temporária, então não deixei nenhum `maze.txt` no projeto. Não alterei o `.gitignore` (está previsto na Task 10).
- **`PERFECT=False`.** O `config.txt` atual pede o modo não-perfeito, mas o programa ainda gera um labirinto perfeito (Task 6). Para esse arquivo o analisador responde "perfeito", o que só bate com `PERFECT=True`.
- **O `pprint` do `main.py`** continua imprimindo todas as células no terminal; não mexi nisso.
