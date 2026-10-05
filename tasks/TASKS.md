# Tasks — A-Maze-ing (parte mandatória)

Marcador de avanço do projeto. Uma task é uma feature com início, meio e fim.
Só avançamos para a próxima quando a atual estiver pronta.

Legenda: `[x]` pronta · `[ ]` pendente

---

## Núcleo do labirinto

- [x] **Task 0 — Parser do config**
  - Lê o arquivo `KEY=VALUE`, ignora comentários, valida as chaves obrigatórias, os limites e `ENTRY != EXIT`.
  - Depende de: nada.
  - Pronta quando: config inválido gera mensagem clara, config válido vira um dicionário.

- [ ] **Task 1 — Grid do labirinto**
  - Estrutura que guarda as células, cada uma com 4 paredes (N, E, S, W), todas fechadas no início.
  - Operações básicas: consultar uma célula, listar vizinhos dentro dos limites, abrir a parede entre duas células vizinhas (sempre dos dois lados).
  - Depende de: nada.
  - Pronta quando: dá para criar um grid WxH, abrir uma parede e ver que as duas células concordam.

- [ ] **Task 2 — Padrão "42"**
  - Marca no centro do grid as células que desenham o "42"; elas ficam totalmente fechadas e o gerador não pode entrar nelas.
  - Se o labirinto for pequeno demais, ou se a entrada/saída cair em cima do desenho, o padrão é omitido com uma mensagem de erro no console.
  - Depende de: Task 1.
  - Pronta quando: as células do "42" estão marcadas no lugar certo e os casos de omissão imprimem o aviso.

- [ ] **Task 3 — Geração do labirinto perfeito (com seed)**
  - Algoritmo que abre paredes até todas as células (fora o "42") estarem conectadas, sem nenhum loop.
  - A mesma seed gera sempre o mesmo labirinto.
  - Depende de: Task 1, Task 2.
  - Pronta quando: toda célula fora do "42" é alcançável, as bordas externas continuam fechadas e duas execuções com a mesma seed dão o mesmo resultado.

- [ ] **Task 4 — Caminho mais curto**
  - Busca em largura (BFS) da entrada até a saída, devolvendo o caminho como letras `N`, `E`, `S`, `W`.
  - Depende de: Task 1 (para testar de verdade: Task 3).
  - Pronta quando: seguir as letras a partir da entrada chega na saída sem atravessar parede.

- [ ] **Task 5 — Arquivo de saída**
  - Escreve o grid em hexadecimal (bit 0 = N, 1 = E, 2 = S, 3 = W; bit 1 = parede fechada), uma linha por fileira.
  - Depois de uma linha vazia: entrada, saída e o caminho mais curto. Toda linha termina com `\n`.
  - Depende de: Task 3, Task 4.
  - Pronta quando: `python3 maze_analyzer.py maze.txt` aceita o arquivo e reporta um labirinto perfeito e coerente.

- [ ] **Task 6 — Modo não-perfeito (`PERFECT=False`)**
  - Parte do labirinto perfeito e abre paredes extras para virar um tabuleiro tipo Pac-Man.
  - Regras: os quatro cantos e o centro são corredores abertos, pelo menos 2 rotas independentes (loops), poucos dead-ends, nenhuma área aberta 3x3.
  - Depende de: Task 3 (para validar: Task 5).
  - Pronta quando: o `maze_analyzer.py` reporta o arquivo como tabuleiro jogável.

- [ ] **Task 7 — Classe `MazeGenerator`**
  - Classe única que junta as Tasks 1 a 6: recebe tamanho, entrada, saída, perfect e seed; gera o labirinto; dá acesso à estrutura e ao caminho.
  - Fica no módulo `mazegen`, sem depender do parser nem do terminal.
  - Depende de: Task 3, Task 4, Task 6.
  - Pronta quando: um script de 5 linhas importa a classe, gera um labirinto e lê o caminho.

## Programa

- [ ] **Task 8 — Render no terminal**
  - Desenha o labirinto em ASCII mostrando paredes, entrada, saída, o "42" e, opcionalmente, o caminho.
  - Depende de: Task 1, Task 4.
  - Pronta quando: o desenho bate com o arquivo de saída e o "42" é visível.

- [ ] **Task 9 — Menu interativo e `a_maze_ing.py` completo**
  - Liga tudo: parser → gerador → arquivo de saída → render.
  - Interações: gerar outro labirinto, mostrar/esconder o caminho, trocar a cor das paredes, sair.
  - Nenhum erro derruba o programa (arquivo inexistente, config ruim, parâmetros impossíveis, Ctrl+C, entrada inválida no menu).
  - Depende de: Task 0, Task 5, Task 7, Task 8.
  - Pronta quando: `python3 a_maze_ing.py config.txt` roda do início ao fim e as três interações funcionam.

## Entrega

- [ ] **Task 10 — Makefile e lint**
  - Regras `install`, `run`, `debug`, `clean`, `lint` (e `lint-strict` opcional); `.gitignore` cobrindo os artefatos de Python.
  - Depende de: nada (o `run` só faz sentido completo depois da Task 9).
  - Pronta quando: `make lint` passa sem erros de flake8 e mypy.

- [ ] **Task 11 — Pacote `mazegen` instalável**
  - `pyproject.toml` e o que mais for preciso para gerar `mazegen-*.whl` / `.tar.gz`, com o arquivo gerado na raiz do repositório.
  - Depende de: Task 7.
  - Pronta quando: num virtualenv limpo, o pacote é construído das fontes, instalado com `pip` e importado.

- [ ] **Task 12 — `LICENSE.md`**
  - Escolher e escrever a licença, que precisa permitir reuso e distribuição do gerador.
  - Depende de: nada.
  - Pronta quando: o arquivo está na raiz e você sabe explicar a escolha.

- [ ] **Task 13 — `README.md`**
  - Primeira linha obrigatória em itálico; seções Description, Instructions e Resources (com o uso de IA).
  - Formato do config, algoritmo escolhido e por quê, o que é reutilizável e como usar o `mazegen`, gestão do projeto.
  - Depende de: todas as anteriores.
  - Pronta quando: alguém de fora consegue rodar o projeto e usar o módulo só lendo o README.
