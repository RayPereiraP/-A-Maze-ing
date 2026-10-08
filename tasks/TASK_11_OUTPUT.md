# Task 11 — Output

Implementação da Task 11 do [TASKS.md](TASKS.md): o pacote `mazegen` instalável com `pip`, com os arquivos gerados na raiz do repositório. Não havia um `TASK_11.md`, então segui o `TASKS.md` e o capítulo VI do subject. O `TASKS.md` não foi alterado.

## Resultado

- `mazegen-1.0.0-py3-none-any.whl` e `mazegen-1.0.0.tar.gz` estão na raiz do repositório.
- Num virtualenv limpo, o pacote foi construído das fontes, instalado com `pip` e importado. Fiz isso com os dois arquivos, o `.whl` e o `.tar.gz`.
- Os 96 testes continuam passando; `make lint` e `make lint-strict` continuam limpos, inclusive depois de um build.

O teu Windows não tem `make`, e o Python de `tmp/parser-runtime` não tem o módulo `venv`. Por isso o build e a instalação foram feitos num container Linux descartável (`python:3.12-slim`), sobre uma cópia do projeto; os dois arquivos gerados foram copiados de lá para a raiz. O pacote é Python puro, então o mesmo arquivo serve em qualquer sistema.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `pyproject.toml` | novo: a receita do pacote |
| `MANIFEST.in` | novo: deixa a pasta `tests/` fora do `.tar.gz` |
| `src/mazegen/README.md` | novo: a documentação curta do módulo |
| `src/mazegen/py.typed` | novo, vazio: avisa o `mypy` que o pacote tem type hints |
| `src/mazegen/*.py` | os imports internos passaram a ser relativos; o docstring do `__init__.py` ganhou um exemplo |
| `Makefile` | nova regra `build`; o `clean` também apaga `build/` e `mazegen.egg-info/` |
| `requirements.txt` | mais uma linha: `build` |
| `mazegen-1.0.0-py3-none-any.whl`, `mazegen-1.0.0.tar.gz` | novos: o pacote construído |

## O `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0.0"
description = "Reusable maze generator of the A-Maze-ing project."
readme = "src/mazegen/README.md"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools]
packages = ["mazegen"]

[tool.setuptools.package-dir]
mazegen = "src/mazegen"

[tool.setuptools.package-data]
mazegen = ["py.typed"]
```

| Bloco | O que diz |
|-------|-----------|
| `[build-system]` | quem constrói o pacote: o `setuptools`. O `pip` e o `build` leem isto primeiro |
| `[project]` | a identidade: nome, versão, descrição, Python mínimo e dependências (nenhuma) |
| `readme` | o texto que vai dentro do pacote como documentação |
| `packages` + `package-dir` | o pacote instalado chama-se `mazegen` e o código dele está em `src/mazegen` |
| `package-data` | arquivos que não são `.py` e também entram: o `py.typed` |

O nome dos arquivos gerados sai daqui: `name` + `version` dão `mazegen-1.0.0`. No `.whl`, `py3-none-any` significa "qualquer Python 3, sem código compilado, qualquer sistema".

## Como funciona

### O que é cada arquivo gerado

- **`.tar.gz`** (sdist): as fontes compactadas, com o `pyproject.toml`. Para instalar, o `pip` tem de construir o pacote primeiro.
- **`.whl`** (wheel): o pacote já construído. É um zip; o `pip` só copia o conteúdo para o `site-packages`.

O subject aceita qualquer um dos dois. `python3 -m build` gera os dois: primeiro o `.tar.gz`, depois o `.whl` a partir dele.

### O que tem dentro do `.whl`

```
mazegen/README.md
mazegen/__init__.py
mazegen/cell.py
mazegen/generator.py
mazegen/map.py
mazegen/maze_generator.py
mazegen/py.typed
mazegen/solver.py
mazegen/writer.py
mazegen-1.0.0.dist-info/METADATA
mazegen-1.0.0.dist-info/WHEEL
mazegen-1.0.0.dist-info/top_level.txt
mazegen-1.0.0.dist-info/RECORD
```

Só a pasta `mazegen`. O `parser.py`, o `renderer.py`, o `main.py` e os testes ficam de fora: são o programa, não o módulo reutilizável. É a mesma separação da Task 7.

### Os imports relativos

Esta foi a única mudança no código. Antes, dentro do `mazegen`:

```python
from src.mazegen.map import Map, Position
```

Depois de instalado, o pacote chama-se `mazegen`, não `src.mazegen`: não existe nenhum `src` no `site-packages`, e esse import quebraria com `ModuleNotFoundError`. Agora:

```python
from .map import Map, Position
```

O ponto significa "do mesmo pacote em que este arquivo está". Funciona nos dois casos: dentro do projeto, onde o pacote é `src.mazegen`, e instalado, onde é `mazegen`. Foram 15 linhas de import em 6 arquivos; nenhuma lógica mudou.

O resto do projeto (`src/main.py`, `src/renderer.py`, os testes) continua a importar `src.mazegen`, direto das fontes. O programa não precisa do pacote instalado para rodar.

### A documentação

O subject pede uma documentação curta, dentro do pacote, que explique como instanciar, passar parâmetros e acessar a estrutura e uma solução. Ela está em [src/mazegen/README.md](../src/mazegen/README.md), em inglês, e vai parar em três lugares:

- dentro do `.whl`, como `mazegen/README.md` e como texto do `METADATA`;
- dentro do `.tar.gz`;
- no docstring do `__init__.py` há um exemplo curto, que aparece com `help(mazegen)`.

O subject pede que o `README.md` principal também tenha essa documentação: isso fica para a Task 13.

### A regra `build`

```make
build:
	$(PYTHON) -m build --outdir .
```

Por padrão o `build` põe os arquivos em `dist/`. O `--outdir .` manda pôr na raiz, que é onde o subject os quer. O build deixa para trás duas pastas temporárias, `build/` e `mazegen.egg-info/`; as duas estão no `.gitignore` e o `make clean` apaga-as.

## Decisões que tomei

- **`setuptools` como construtor.** É o padrão, e é o que o subject descreve como "standard build of a Python package".
- **Versão `1.0.0`**, como no exemplo do subject.
- **O código continua em `src/mazegen`.** O `package-dir` faz a ponte, sem mover nenhum arquivo.
- **Gerei os dois formatos.** O subject pede um; ter os dois não custa nada e o `.tar.gz` prova que dá para reconstruir das fontes.
- **`py.typed` incluído.** É um arquivo vazio. Sem ele, o `mypy` de um projeto futuro trataria o `mazegen` como biblioteca sem tipos. Não é exigido pelo subject; se preferires, basta apagar o arquivo e o bloco `package-data`.
- **`MANIFEST.in` com `prune tests`.** O `setuptools` põe `tests/test*.py` no `.tar.gz` por conta própria. Esses testes importam `src.parser` e `src.renderer`, que não estão no pacote, então lá dentro não rodariam.
- **A regra `build` entrou no `Makefile`** e o `build` entrou no `requirements.txt`, porque na avaliação vão pedir para reconstruir o pacote.
- **Sem campo `license` no `pyproject.toml`.** A licença é a Task 12. Quando o `LICENSE.md` existir na raiz, o `setuptools` inclui-o no pacote sozinho no build seguinte.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "num virtualenv limpo, o pacote é construído das fontes, instalado com `pip` e importado".

O que rodei no container, nesta ordem:

| Passo | Comando | Resultado |
|-------|---------|-----------|
| venv de build | `python3 -m venv /venv`, `make install` | `flake8`, `mypy` e `build` instalados |
| construir | `make build` | `Successfully built mazegen-1.0.0.tar.gz and mazegen-1.0.0-py3-none-any.whl` |
| venv limpo | `python3 -m venv /clean` | sem nada além do `pip` |
| instalar o `.whl` | `pip install mazegen-1.0.0-py3-none-any.whl` | instalado |
| importar | `from mazegen import MazeGenerator`, a partir de `/`, fora do projeto | veio de `/clean/lib/python3.12/site-packages/mazegen/` |
| usar | `MazeGenerator(15, 20, (0, 0), (14, 19), True, 42).path` | 165 letras, o mesmo caminho que as fontes dão na tua máquina |
| instalar o `.tar.gz` | o mesmo, noutro venv limpo | mesmo resultado |
| tipos | `mypy --strict` num script que importa `mazegen` | sem erros; `generator.path` é `str` |
| lint depois do build | `make lint` | `Success: no issues found in 22 source files` |
| limpar | `make clean` | `build/` e `mazegen.egg-info/` apagados |

O import foi feito de propósito a partir de `/`, e não da pasta do projeto: assim é certo que o `mazegen` usado é o instalado, e não as fontes ao lado.

## Como rodar

Num Linux ou macOS, na raiz do projeto:

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
make build

# num outro virtualenv, para testar:
python3 -m venv /tmp/clean
/tmp/clean/bin/pip install mazegen-1.0.0-py3-none-any.whl
cd / && /tmp/clean/bin/python -c "from mazegen import MazeGenerator; print(MazeGenerator(15, 20, (0, 0), (14, 19)).path)"
```

No teu Windows, com Docker, sem instalar nada:

```powershell
docker run --rm -v "${PWD}:/repo" -w /repo python:3.12-slim sh -c "pip install -q build && python3 -m build --outdir ."
```

Este último comando eu não rodei exatamente assim: usei uma cópia do projeto dentro do container e copiei os dois arquivos de volta.

## Pontos de atenção

- **Os dois arquivos gerados têm de ser commitados.** O subject exige o `mazegen-*` na raiz do repositório. Não fiz commit de nada.
- **Mudou o código do `mazegen`? Reconstrói.** O `.whl` é uma cópia do código no momento do build; não se atualiza sozinho. Antes da entrega, roda `make build` uma última vez (e de novo depois da Task 12, para a licença entrar).
- **O `mazegen` escreve no `stderr`.** O aviso do "42" omitido é impresso pelo `Map`. Num projeto futuro que use o pacote, esse aviso vai aparecer no terminal dele. Está documentado no README do módulo; não alterei esse comportamento.
- **As posições são `(row, col)` no módulo e `x,y` no arquivo de saída.** Quem reutilizar o pacote precisa saber disso; o README do módulo diz.
- **O build foi feito com Python 3.12**, o do container. O pacote declara `>=3.10` e os testes rodam em 3.10 na tua máquina, mas a instalação do `.whl` só foi testada em 3.12.
