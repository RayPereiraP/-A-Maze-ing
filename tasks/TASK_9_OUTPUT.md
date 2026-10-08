# Task 9 — Output

Implementação da Task 9 do [TASKS.md](TASKS.md): o menu interativo e o `a_maze_ing.py` completo, ligando parser → gerador → arquivo de saída → render. Não havia um `TASK_9.md`, então segui o `TASKS.md` e os capítulos IV.2 e V do subject. O `TASKS.md` não foi alterado.

## Resultado

- 96 testes, 96 passando (77 das Tasks 1 a 8 + 19 novos).
- `flake8` sem avisos e `mypy` sem erros com as flags do subject.
- `python3 a_maze_ing.py config.txt` roda do início ao fim: escreve o arquivo, desenha o labirinto e fica no menu até a opção 4.
- O `maze_analyzer.py` aceita o arquivo escrito depois de um "Re-generate" (10x10 do `config.txt` atual: coerente e "Pac-Man-USABLE").

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `src/main.py` | reescrito: `build_generator`, `clear_screen`, `regenerate`, `run_menu`, `main` |
| `src/renderer.py` | `render_maze` ganhou o parâmetro `wall_color`; nova função `paint` |
| `tests/test_main.py` | novo: 19 testes |

Nada dentro de `src/mazegen/` nem em `src/parser.py` foi alterado. O `a_maze_ing.py` da raiz também não: ele já só chamava `main()`.

## O que aparece no terminal

```
+---+---+---+---+---+---+---+---+---+---+
| E                     |               |
+   +   +---+   +   +   +   +---+   +   +
|   |           |                       |
...
|                           |         X |
+---+---+---+---+---+---+---+---+---+---+
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
Choice? (1-4):
```

| Opção | O que faz |
|-------|-----------|
| 1 | gera outro labirinto, reescreve o arquivo de saída e desenha de novo |
| 2 | liga/desliga os ` o ` do caminho mais curto |
| 3 | passa para a próxima cor de parede |
| 4 | sai com código 0 |

O texto do menu é o mesmo da figura do capítulo V do subject.

## Código

O laço do menu, em `src/main.py`:

```python
def run_menu(generator: MazeGenerator, output_file: str) -> None:
    show_path = False
    color_index = 0
    while True:
        print(render_maze(
            generator.maze_map, show_path, WALL_COLORS[color_index]
        ))
        print(MENU)
        choice = input("Choice? (1-4): ").strip()
        while choice not in ("1", "2", "3", "4"):
            print("Invalid choice: type a number from 1 to 4.")
            choice = input("Choice? (1-4): ").strip()
        if choice == "4":
            return
        # Cleared before the action, so a message it prints stays visible.
        clear_screen()
        if choice == "1":
            regenerate(generator, output_file)
        elif choice == "2":
            show_path = not show_path
        else:
            color_index = (color_index + 1) % len(WALL_COLORS)
```

A limpeza da tela:

```python
CLEAR_SCREEN = "\033[2J\033[3J\033[H"


def clear_screen() -> None:
    print(CLEAR_SCREEN, end="", flush=True)
```

O "gerar outro":

```python
def regenerate(generator: MazeGenerator, output_file: str) -> None:
    if generator.seed is not None:
        generator.seed += 1
    generator.generate()
    generator.write(output_file)
```

A cor, em `src/renderer.py`:

```python
def paint(text: str, color: str) -> str:
    if not color:
        return text
    return color + text + RESET_COLOR
```

## Como funciona

### O fluxo do `main`

1. `parse_config` lê e valida o arquivo (Task 0).
2. `build_generator` troca `(x, y)` do config por `(row, col)` e cria o `MazeGenerator`, que já gera o primeiro labirinto (Task 7).
3. `generator.write` escreve o arquivo de saída (Task 5).
4. `run_menu` desenha (Task 8) e espera as escolhas.

O arquivo é escrito **antes** do menu. Se o usuário sair com Ctrl+C logo no início, o arquivo já existe.

### O estado do menu são duas variáveis

`show_path` (liga/desliga) e `color_index` (posição na lista `WALL_COLORS`). O labirinto em si mora no `generator`. Cada volta do `while True` desenha tudo de novo a partir dessas três coisas, então nenhuma opção precisa saber desenhar: ela só muda o estado e o laço redesenha.

Por isso o caminho continua ligado e a cor continua a mesma depois de um "Re-generate".

### A tela é limpa antes de cada desenho

Pedido teu depois da primeira versão: sem isso, cada interação empilhava mais um desenho no terminal.

`CLEAR_SCREEN` são três códigos ANSI, do mesmo tipo dos das cores: `\033[2J` apaga a tela, `\033[3J` apaga o histórico de rolagem e `\033[H` leva o cursor para o canto de cima.

A limpeza acontece em dois lugares:

- no `main`, logo antes de criar o gerador (o primeiro desenho);
- no `run_menu`, depois de uma escolha válida e **antes** de executar a ação.

Ela vem antes da ação, e não logo antes do `print` do desenho, por causa do aviso do "42" omitido: quem o imprime é o `Map`, durante a geração. Se a tela fosse limpa depois de gerar, o aviso seria apagado antes de alguém ler. Do jeito que está, ele aparece em cima do desenho novo.

O `flush=True` existe porque o código não termina com `\n`: sem ele, o Python poderia segurar a limpeza no buffer e só enviá-la depois do aviso, apagando-o.

A opção 4 não limpa: o último labirinto fica na tela ao sair. Uma escolha inválida também não: só aparece a mensagem e a pergunta de novo.

### Escolha inválida

O `while` de dentro repete só a pergunta, sem redesenhar o labirinto. O `.strip()` aceita `" 2 "`. Linha vazia, `0`, `5` e `abc` caem na mensagem `Invalid choice`.

### "Re-generate" com seed

O `generate()` com a mesma seed devolve sempre o mesmo labirinto (é a regra da Task 3). Então, para sair um labirinto novo, `regenerate` soma 1 à seed antes. Com `SEED=7` a sequência de uma execução é sempre 7, 8, 9...: continua reproduzível. Sem `SEED` no config, a seed é `None` e cada geração já é aleatória.

### A cor

Uma cor no terminal é um código ANSI: `\033[31m` liga o vermelho e `\033[0m` desliga. O `render_maze` pinta, uma vez só no início, os três pedaços que são parede (`+`, `---`, `|`) e usa esses pedaços já pintados no resto da função. O conteúdo das células (` E `, ` X `, `###`, ` o `) e as paredes abertas nunca levam cor.

Com `wall_color=""` (o padrão) o `paint` devolve o texto como está, então o desenho é idêntico ao da Task 8 e os testes antigos continuam valendo.

## Erros tratados

O subject (IV.2) pede que o programa nunca caia e sempre dê uma mensagem clara. Todos os `except` estão no `main`, num lugar só:

| Situação | De onde vem | Mensagem | Código |
|----------|-------------|----------|--------|
| nenhum argumento, ou mais de um | `main` | `Usage: python3 a_maze_ing.py config.txt` | 1 |
| arquivo de config inexistente ou ilegível | `ConfigError` | `Error: Cannot read '...'` | 1 |
| linha sem `=`, chave repetida, valor ruim | `ConfigError` | `Error: Line N: ...` | 1 |
| `WIDTH=0`, entrada/saída fora do mapa, entrada = saída | `ConfigError` | `Error: ...` | 1 |
| arquivo de saída não pode ser escrito | `OSError` | `Error: cannot write the output file: ...` | 1 |
| gerador recusa os parâmetros | `ValueError` | `Error: impossible maze parameters: ...` | 1 |
| labirinto grande demais para a memória | `MemoryError` | `Error: the maze is too big for the memory.` | 1 |
| Ctrl+C, Ctrl+D ou fim de uma entrada por pipe | `KeyboardInterrupt`, `EOFError` | nenhuma (só uma quebra de linha) | 0 |
| escolha inválida no menu | `run_menu` | `Invalid choice: type a number from 1 to 4.` | continua |

As mensagens de erro vão para o `stderr`; o desenho e o menu, para o `stdout`.

## Decisões que tomei

- **O menu ficou no `main.py`**, sem um arquivo novo. São quatro funções pequenas e o `main.py` continua com cerca de 130 linhas.
- **O caminho começa escondido.** É como a figura "Terminal default rendering" do subject. Na Task 8 o `main` passava `show_path=True` só para dar para ver; agora é a opção 2.
- **Tirei a linha com as letras do caminho** que o `main` imprimia depois do desenho. As letras continuam no arquivo de saída.
- **"Re-generate" reescreve o arquivo de saída.** Assim o arquivo sempre corresponde ao labirinto que está na tela.
- **A seed anda de 1 em 1**, em vez de virar `None`. Mantém a execução reproduzível, que é o que o subject pede da seed.
- **Sete cores, em roda:** padrão do terminal, vermelho, verde, amarelo, azul, magenta, ciano. A lista `WALL_COLORS` fica no topo do `main.py`.
- **A cor entra no `render_maze` como um código ANSI qualquer**, não como um nome. O renderer não conhece a lista de cores; quem escolhe é o menu.
- **A tela é limpa com códigos ANSI, não com `os.system("cls")`/`"clear"`.** É o mesmo mecanismo das cores, não depende do sistema operacional e passa pelo `stdout`, então dá para testar.
- **Um erro depois da limpeza aparece numa tela vazia.** Por exemplo, se o arquivo de saída não puder ser escrito, a tela já foi limpa e fica só a mensagem de erro. Erros de config acontecem antes da limpeza e não apagam nada.
- **Não mexi no "42":** continua `###` sem cor própria. A cor do "42" é o item opcional do capítulo V.
- **Ctrl+C devolve 0**, sem mensagem: é o usuário saindo, não um erro.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "`python3 a_maze_ing.py config.txt` roda do início ao fim e as três interações funcionam".

| Critério | Teste que cobre |
|----------|-----------------|
| Roda do início ao fim | `test_runs_from_start_to_end` |
| Gerar outro labirinto | `test_regenerate_draws_and_writes_another_maze`, `test_regenerate_without_seed_gives_a_valid_maze` |
| Mostrar/esconder o caminho | `test_path_is_hidden_then_shown_then_hidden`, `test_path_stays_shown_after_regenerating` |
| Trocar a cor das paredes | `test_wall_colours_rotate_and_come_back`, `test_removing_the_codes_gives_the_plain_drawing`, `test_only_walls_are_coloured` |
| Tela limpa antes de cada desenho | `test_screen_is_cleared_before_each_drawing`, `test_invalid_choice_does_not_clear_the_screen` |
| Entrada inválida no menu | `test_invalid_choices_are_asked_again` |
| Arquivo inexistente | `test_missing_config_file` |
| Config ruim | `test_bad_syntax`, `test_wrong_number_of_arguments` |
| Parâmetros impossíveis | `test_impossible_parameters`, `test_generator_refusing_the_parameters` |
| Arquivo de saída sem permissão/pasta | `test_output_file_cannot_be_written` |
| Ctrl+C e fim da entrada | `test_ctrl_c_and_end_of_input_leave_quietly` |
| Labirinto pequeno, sem "42" | `test_small_maze_omits_the_42_and_still_runs` |

Os testes rodam o `main()` de verdade numa pasta temporária. As respostas do menu são dadas trocando o `input` por uma lista (`patch("builtins.input", side_effect=[...])`); uma exceção na lista, como `KeyboardInterrupt()`, é levantada no lugar da resposta. Se o menu pedir mais respostas do que a lista tem, o teste falha, então um menu que não sai é percebido.

Os testes do menu comparam o `stdout` com o esperado, montado com `render_maze` e `MENU`. Os códigos de limpeza são retirados antes dessa comparação e verificados à parte, nos dois testes da tela limpa. Por exemplo, para `["2", "2", "4"]` a saída tem de ser exatamente: desenho sem caminho, desenho com caminho, desenho sem caminho.

Além dos testes, rodei o programa de verdade com as respostas por pipe (`2`, `4`) e o caminho apareceu; e com `3`, `1`, `4` seguido do `maze_analyzer.py` no arquivo gerado.

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

- **Não testei o menu digitando à mão num terminal.** Tudo o que rodei foi com respostas por pipe ou pelo `patch` do `input`. Vale abrir o programa e apertar 1, 2, 3 e 4 para ver as cores de verdade.
- **Cores e limpeza em terminais antigos do Windows.** Os códigos ANSI funcionam no terminal do VS Code, no Windows Terminal e no Linux. No console antigo do Windows (`conhost`) podem aparecer como texto (`←[31m`). Não tratei isso.
- **O `MemoryError` não foi testado.** O `except` está lá, mas não gerei um labirinto gigante para confirmar; antes de faltar memória, o programa fica muito tempo ocupado criando células.
- **Largura do terminal.** Continua como na Task 8: 4 caracteres por coluna, sem tratamento para labirintos mais largos que a janela.
- **O `ValueError` do gerador não acontece hoje pelo caminho normal**, porque o parser já recusa os mesmos casos antes. O `except` fica como rede de segurança, e o teste dele troca o `MazeGenerator` por um que falha.
- **O aviso do "42" omitido aparece a cada "Re-generate"** em labirintos pequenos, porque é o `Map` que o imprime ao ser criado.
- **Rodar o programa reescreveu o `maze.txt` da raiz** (é o `OUTPUT_FILE` do `config.txt`). Ele já aparecia como modificado no `git status` antes.
