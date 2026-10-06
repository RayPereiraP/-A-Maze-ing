# Task 4 — Output

Implementação da Task 4 do [TASKS.md](TASKS.md): o caminho mais curto da entrada até a saída, por busca em largura (BFS), devolvido como letras `N`, `S`, `E`, `W`. Não havia um `TASK_4.md`, então segui a descrição e o "Pronta quando" do `TASKS.md`.

## Resultado

- 38 testes, 38 passando (29 das Tasks 1 a 3 + 9 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- `a_maze_ing.py config.txt` roda sem erro e imprime o caminho na última linha. Com o `config.txt` atual (5x7, seed 2) o caminho é `SSSENESSWSWSEEEE`.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/mazegen/solver.py` | novo: função `shortest_path` |
| `src/mazegen/__init__.py` | exporta `shortest_path` |
| `src/main.py` | chama `shortest_path` depois do gerador e imprime o caminho no final |
| `tests/test_solver.py` | novo: 9 testes |

`Cell`, `Map` e o gerador não foram alterados.

## Código

```python
def shortest_path(maze_map: Map) -> str:
    if maze_map.entry is None or maze_map.exit is None:
        raise ValueError("The map needs an entry and an exit.")
    entry: Position = maze_map.entry
    exit: Position = maze_map.exit

    # cell -> (cell it was reached from, direction of that step)
    came_from: Dict[Position, Tuple[Position, str]] = {}
    queue: Deque[Position] = deque([entry])
    while queue:
        current = queue.popleft()
        if current == exit:
            break
        row, col = current
        for direction, (row_delta, col_delta, _) in DIRECTIONS.items():
            if getattr(maze_map.cell(row, col), direction):
                continue
            neighbour = (row + row_delta, col + col_delta)
            if neighbour == entry or neighbour in came_from:
                continue
            came_from[neighbour] = (current, direction)
            queue.append(neighbour)
    if exit != entry and exit not in came_from:
        raise ValueError("The exit cannot be reached from the entry.")

    for cells in maze_map.grid:
        for cell in cells:
            cell.path = False
    # Walk back from the exit to the entry, then reverse the letters.
    letters: List[str] = []
    current = exit
    maze_map.cell(*current).path = True
    while current != entry:
        current, direction = came_from[current]
        letters.append(direction)
        maze_map.cell(*current).path = True
    return "".join(reversed(letters))
```

## Como funciona

A função tem duas metades: a busca, que descobre como chegar em cada célula, e a reconstrução, que monta as letras.

### Metade 1: a busca em largura

A BFS se espalha a partir da entrada como água: primeiro todas as células a 1 passo, depois todas a 2 passos, depois a 3, e assim por diante. Por isso, na primeira vez que ela chega na saída, chegou pelo menor número de passos possível.

1. Põe a entrada na fila.
2. Tira a célula mais antiga da fila (`popleft`).
3. Se for a saída, para.
4. Para cada uma das quatro direções: se a parede está fechada, ignora. Se a vizinha já foi alcançada antes, ignora.
5. Caso contrário, anota em `came_from` de onde a vizinha foi alcançada e com qual letra, e põe a vizinha no fim da fila.
6. Volta ao passo 2.

### A fila, e a diferença para a Task 3

O gerador da Task 3 usa uma **pilha**: pega sempre a célula mais **nova** (`stack[-1]`), então vai fundo num corredor antes de voltar. A BFS usa uma **fila**: pega sempre a célula mais **antiga** (`popleft`), então termina uma distância inteira antes de começar a próxima. Essa única diferença é o que garante o caminho mais curto.

Usei `collections.deque` porque tirar do início de uma `list` (`pop(0)`) desloca todos os outros elementos, e o `deque` não.

### O dicionário `came_from`

Ele faz dois trabalhos:

- **Marca quem já foi alcançado.** Uma célula que está em `came_from` não entra na fila de novo. A entrada é a única alcançada sem vir de ninguém, por isso a checagem `neighbour == entry` à parte.
- **Guarda o caminho de volta.** Para cada célula, guarda a célula anterior e a letra do passo.

Não é preciso checar se a vizinha está dentro do mapa ou se é do "42": uma parede aberta nunca leva para fora (Task 1) nem para dentro do "42" (Task 3).

### Metade 2: a reconstrução

A busca sabe, para cada célula, de onde ela veio, mas não para onde ir. Então o caminho é montado de trás para frente: começa na saída, pergunta a `came_from` qual era a anterior e qual foi a letra, e repete até chegar na entrada. As letras saem na ordem inversa, e o `reversed` as desvira.

No mesmo laço, cada célula visitada recebe `path = True`.

## Decisões que tomei

- **A função também marca `cell.path`.** O `TASKS.md` pede só as letras, mas o atributo `path` existe desde a Task 1 e nada o preenchia. A Task 8 (render) vai precisar saber quais células desenhar como caminho, então marquei aqui: entrada e saída incluídas. Antes de marcar, a função põe `path = False` em todas as células, para que uma segunda chamada não deixe marcas antigas.
- **Sem entrada ou sem saída: `ValueError`.** No `Map` as duas são opcionais, mas sem elas não há caminho para procurar.
- **Saída inalcançável: `ValueError`.** Num labirinto gerado pela Task 3 isso nunca acontece. Só acontece num mapa montado à mão, ou sem gerar. Nesse caso nenhuma marca de `path` é alterada.
- **Entrada igual à saída: devolve `""`.** O parser já proíbe esse caso; a função só não quebra.
- **Uma função, não uma classe.** Mesmo motivo da Task 3: a classe que junta tudo é a Task 7.
- **O `main.py` não trata esses `ValueError`.** Com o config validado pelo parser e o labirinto gerado, eles não acontecem. O tratamento geral de erros é a Task 9.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando: "seguir as letras a partir da entrada chega na saída sem atravessar parede".

| Critério | Teste que cobre |
|----------|-----------------|
| Seguir as letras a partir da entrada chega na saída sem atravessar parede | `test_letters_lead_from_entry_to_exit` |
| O caminho é o mais curto (da descrição da task) | `test_takes_the_shorter_of_two_routes` |

`test_letters_lead_from_entry_to_exit` roda em 4 tamanhos de mapa com 5 seeds cada (20 labirintos). Ele anda letra por letra, falha se a parede daquela direção estiver fechada, e confere que a última célula é a saída.

Num labirinto perfeito só existe um caminho, então ele não prova que a BFS escolhe o mais curto. Para isso, `test_takes_the_shorter_of_two_routes` monta à mão um mapa 3x3 com duas rotas até a saída, uma de 2 passos e outra de 4, e espera `"EE"`.

Testes além dos critérios:

- `test_takes_the_only_route`: num 2x2 com uma única rota em volta, o resultado é `"SEN"`.
- `test_marks_exactly_the_cells_of_the_path`: as células com `path == True` são exatamente as do caminho.
- `test_second_call_clears_old_marks`: uma marca antiga fora do caminho é apagada.
- `test_does_not_change_walls_or_42`: a função não mexe em paredes nem em `is_42`.
- `test_entry_equal_to_exit`, `test_missing_entry_or_exit`, `test_unreachable_exit`: os casos de borda e os dois erros.

## Verificação visual

Mapa 9x13, entrada `(0, 0)`, saída `(8, 12)`, seed 42. `o` são as células com `path == True` e `###` são as do "42":

```
+---+---+---+---+---+---+---+---+---+---+---+---+---+
| o | o   o |   |       |                           |
+   +   +   +   +   +   +   +---+---+---+   +---+   +
| o | o | o |       |                   |       |   |
+   +   +   +---+   +---+   +---+---+---+---+   +   +
| o   o | o |###|   |###|   |###|###|###|       |   |
+---+---+   +---+   +---+   +---+---+---+   +---+   +
|       | o |###|   |###|           |###|       |   |
+   +   +   +---+---+---+   +---+---+---+---+   +   +
|   |   | o |###|###|###|   |###|###|###|       |   |
+   +---+   +---+---+---+   +---+---+---+   +---+---+
|       | o |       |###|   |###|                   |
+---+   +   +   +---+---+   +---+---+---+   +---+   +
|       | o |       |###|   |###|###|###|       |   |
+   +   +   +---+   +---+   +---+---+---+   +---+   +
|   |   | o | o   o |       | o   o   o |   | o   o |
+   +---+   +   +   +---+---+   +---+   +---+   +   +
|         o   o | o   o   o   o |     o   o   o | o |
+---+---+---+---+---+---+---+---+---+---+---+---+---+
```

Caminho devolvido, com 30 passos:

```
SSENNESSSSSSSSENESEEENEESEENES
```

O desenho foi feito por um script temporário, fora do projeto. O render de verdade é a Task 8.

## Como rodar

Na raiz do projeto:

```powershell
.\tmp\parser-runtime\python.exe -m unittest discover -s tests -t . -v
.\tmp\parser-runtime\python.exe -m flake8 src tests a_maze_ing.py
.\tmp\parser-runtime\python.exe -m mypy src tests a_maze_ing.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

Não rodei pelo Docker.

## Pontos de atenção

- **Ordem das letras.** O `TASKS.md` escreve `N`, `E`, `S`, `W`; o código percorre `DIRECTIONS` como `N`, `S`, `E`, `W`. Isso não muda o tamanho do caminho. Só importa quando existem dois caminhos mais curtos de mesmo tamanho (possível no modo não-perfeito, Task 6): aí a ordem decide qual dos dois é devolvido.
- **Modo não-perfeito.** Quando a Task 6 abrir paredes extras, `shortest_path` precisa ser chamada depois dela, porque o caminho mais curto pode mudar.
- **Coordenadas.** O caminho é só letras, então não tem o problema de `(x, y)` contra `(row, col)`. A entrada e a saída no arquivo de saída (Task 5) ainda precisam ser escritas como `x,y`.
