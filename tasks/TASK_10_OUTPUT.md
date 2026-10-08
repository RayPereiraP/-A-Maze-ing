# Task 10 — Output

Implementação da Task 10 do [TASKS.md](TASKS.md): o `Makefile` com as regras do subject e o `.gitignore` cobrindo os artefatos de Python. Não havia um `TASK_10.md`, então segui o `TASKS.md` e os capítulos III.2 e III.3 do subject. O `TASKS.md` não foi alterado.

## Resultado

- `make lint` passa: `flake8 .` sem avisos e `mypy .` com as flags do subject sem erros, em 22 arquivos.
- `make lint-strict` também passa (`mypy . --strict`).
- `make install`, `make run`, `make debug` e `make clean` funcionam.
- Os 96 testes continuam passando; nenhum arquivo de código foi alterado.

O teu Windows não tem `make`. Rodei as seis regras com o `make` de verdade num container Linux descartável (`python:3.12-slim`), sobre uma cópia do projeto. Na tua máquina, rodei só os dois comandos do lint diretamente, com o Python de `tmp/parser-runtime`.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `Makefile` | novo: `install`, `run`, `debug`, `clean`, `lint`, `lint-strict` |
| `requirements.txt` | novo: `flake8` e `mypy` |
| `setup.cfg` | novo: pastas que o `flake8 .` e o `mypy .` devem pular |
| `.gitignore` | reescrito: padrões gerais no lugar dos caminhos fixos |

## O Makefile

```make
PYTHON = python3
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache \
		-o -name .pytest_cache \) -prune -exec rm -rf {} +

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict
```

| Regra | O que faz |
|-------|-----------|
| `make install` | instala o `flake8` e o `mypy` com o `pip` |
| `make run` | roda `python3 a_maze_ing.py config.txt` |
| `make debug` | roda o mesmo programa dentro do `pdb` |
| `make clean` | apaga as pastas `__pycache__`, `.mypy_cache` e `.pytest_cache` |
| `make lint` | `flake8 .` e depois `mypy .` com as cinco flags do subject |
| `make lint-strict` | `flake8 .` e depois `mypy . --strict` |

## Como funciona

### Variáveis

`PYTHON` e `CONFIG` ficam no topo e podem ser trocadas na linha de comando, sem editar o arquivo:

```
make run CONFIG=outro.txt
make lint PYTHON=.venv/bin/python
```

`MYPY_FLAGS` guarda as cinco flags que o subject exige no `lint`. A `\` no fim da linha só quebra a linha longa.

### `.PHONY`

O `make` foi feito para construir arquivos: se existir um arquivo chamado `clean` ou `install` na pasta, ele acha que a regra "já está pronta" e não faz nada. O `.PHONY` diz que esses nomes são comandos, não arquivos, e que devem rodar sempre.

### Cada linha de uma regra começa com TAB

Não com espaços. Se o editor trocar o TAB por espaços, o `make` para com `missing separator`.

### `install`

O programa em si só usa a biblioteca padrão do Python. As únicas dependências são as ferramentas do lint, listadas no `requirements.txt`. `python3 -m pip` garante que o `pip` usado é o do mesmo Python que roda o projeto.

### `debug`

`python3 -m pdb a_maze_ing.py config.txt` abre o depurador parado na primeira linha. Os comandos mais úteis: `c` continua, `n` vai para a próxima linha, `s` entra na função, `b src/main.py:80` põe um breakpoint, `p variavel` mostra um valor, `q` sai.

### `clean`

O `find` procura pastas (`-type d`) com um dos três nomes. O `-prune` impede que ele tente entrar numa pasta que vai ser apagada, e o `-exec rm -rf {} +` apaga todas de uma vez. Sem nada para apagar, o comando termina sem erro: dá para rodar `make clean` duas vezes seguidas.

Ele não apaga o `maze.txt`: é o arquivo de saída, e está versionado no git.

### `lint`

São os dois comandos do subject, um por linha. O `make` para na primeira linha que falhar: se o `flake8` acusar algo, o `mypy` nem roda e o `make lint` termina com erro.

### Por que existe um `setup.cfg`

O subject manda rodar `flake8 .` e `mypy .`, ou seja, na pasta inteira. Mas a pasta tem código que não é do projeto:

| Pasta | O que é | O que acontece sem excluir |
|-------|---------|----------------------------|
| `tmp/` | um Python inteiro com as bibliotecas instaladas | milhares de arquivos de terceiros são analisados |
| `42_M02_A-Maze-Ing-main/` | um projeto de referência | tem outro `a_maze_ing.py` e outro `mazegen`; o `mypy` recusa dois módulos com o mesmo nome |
| `.venv/`, `venv/` | ambientes virtuais | o mesmo problema de `tmp/` |
| `build/`, `dist/` | resultado do build do pacote (Task 11) | cópias do código seriam analisadas duas vezes |

O `setup.cfg` é lido sozinho pelas duas ferramentas. Assim a exclusão vale tanto para o `make lint` quanto para quem digitar `flake8 .` direto no terminal, e os comandos do `Makefile` ficam idênticos aos do subject.

```ini
[flake8]
extend-exclude = tmp,.venv,venv,build,dist,42_M02_A-Maze-Ing-main

[mypy]
exclude = ^(tmp|\.venv|venv|build|dist|42_M02_A-Maze-Ing-main)/
```

No `flake8` é `extend-exclude`, e não `exclude`, para somar à lista padrão dele (`.git`, `__pycache__`...) em vez de substituí-la. No `mypy` o valor é uma expressão regular: caminhos que começam com uma dessas pastas.

O `maze_analyzer.py`, que veio com o subject, **não** foi excluído: ele passa nos dois, inclusive no `--strict`.

## O `.gitignore`

Antes eram quatro caminhos fixos (`/tmp` e três `__pycache__`). Agora são padrões que valem em qualquer pasta:

```gitignore
/tmp
__pycache__/
*.py[cod]
.mypy_cache/
.pytest_cache/
.venv/
venv/
build/
dist/
*.egg-info/
```

Conferi com o git: nenhum arquivo já versionado passou a ser ignorado, e `tmp/`, `.mypy_cache/` e os três `__pycache__/` aparecem como ignorados.

`build/`, `dist/` e `*.egg-info/` já ficam prontos para a Task 11. O pacote final (`mazegen-*.whl` ou `.tar.gz`) tem de ficar na **raiz** do repositório, e nenhum desses padrões o ignora lá.

## Decisões que tomei

- **`$(PYTHON) -m flake8 .` em vez de `flake8 .` puro.** É o mesmo comando, mas rodado pelo Python escolhido. O `pip` às vezes instala o executável `flake8` numa pasta que não está no `PATH`; com `-m` isso não importa.
- **`lint-strict` incluída.** É opcional no subject, mas está citada no `TASKS.md` e o código já passa, então custa duas linhas.
- **`install` usa `pip` direto, sem criar ambiente virtual.** Mantém a regra em uma linha. O subject só recomenda o venv; ver o primeiro ponto de atenção.
- **Sem versões fixas no `requirements.txt`.** Só `flake8` e `mypy`.
- **Sem regras a mais** (`all`, `help`, `re`, `test`, `build`). O `build` do pacote entra na Task 11.
- **A exclusão ficou num arquivo de configuração, não em `--exclude` no `Makefile`**, pelo motivo da seção acima.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "`make lint` passa sem erros de flake8 e mypy".

Saída do `make lint` no container:

```
python3 -m flake8 .
python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
Success: no issues found in 22 source files
```

| Regra | Como verifiquei |
|-------|-----------------|
| `install` | instalou `flake8` e `mypy` num Python limpo; o `lint` seguinte só funciona por causa disso |
| `lint` | saída acima, código de saída 0 |
| `lint-strict` | `Success: no issues found in 22 source files`, código 0 |
| `run` | com `2` e `4` por pipe: desenhou o labirinto e o menu |
| `debug` | abriu o `(Pdb)`; com `c` o programa rodou até o menu e saiu com status 0 |
| `clean` | havia 4 pastas de cache; depois, 0; uma segunda chamada também terminou com 0 |

## Como rodar

Num Linux ou macOS (ou nas máquinas da 42), na raiz do projeto:

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
make lint
make run
```

No teu Windows, sem `make`, os comandos equivalentes do lint são:

```powershell
.\tmp\parser-runtime\python.exe -m flake8 .
.\tmp\parser-runtime\python.exe -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

## Pontos de atenção

- **`make install` fora de um venv pode ser recusado.** Em Debian/Ubuntu recentes o `pip` do sistema responde `externally-managed-environment`. Com o venv ativado (bloco acima) funciona. No container não apareceu porque a imagem oficial do Python não tem essa trava.
- **O `Makefile` é para Linux/macOS.** Usa `python3`, `find` e `rm`. No Windows sem `make` ele não roda; é o ambiente da avaliação que conta.
- **A pasta `42_M02_A-Maze-Ing-main/` está versionada no teu repositório.** Só a excluí do lint. Como o subject diz que apenas o que está no repositório é avaliado, vale decidires se um projeto de referência deve ir junto na entrega.
- **O `README.md` atual e o `en.subject.pdf` também estão versionados.** O README é da Task 13; o PDF fica a teu critério.
- **O `requirements.txt` muda o Docker.** O `Dockerfile` já instalava esse arquivo "se existir"; agora a imagem passa a trazer `flake8` e `mypy`. Não reconstruí a imagem do projeto.
- **`make run` e `make debug` reescrevem o `maze.txt`**, como qualquer execução do programa.
