# Executar no terminal com Docker

Este ambiente usa Python 3.12 e um terminal interativo. Nao instala MiniLibX
nem conecta uma janela grafica ao computador.

O projeto ainda precisa de `a_maze_ing.py`, de um arquivo de configuracao e
da implementacao da visualizacao ASCII. O Docker fornece o ambiente de
execucao; ele nao transforma uma interface grafica em uma interface de terminal.

## Requisitos

Docker com suporte ao Compose e containers Linux. No Windows, inicie o
Docker Desktop com o mecanismo de containers Linux antes de executar os comandos.

## Executar

Na raiz do projeto:

```powershell
docker compose build
docker compose run --rm maze
```

O comando executa `python a_maze_ing.py config.txt`. Para outra configuracao:

```powershell
docker compose run --rm maze minha_config.txt
```

Use `docker compose run` para manter o teclado conectado a interface interativa.
O diretorio do projeto e montado em `/app`: alteracoes no codigo ficam
disponiveis no container e arquivos de saida gravados nesse diretorio permanecem
no computador. As dependencias de um eventual `requirements.txt` sao instaladas
durante o build; refaca o build quando elas mudarem.

## Analisar um labirinto existente

O analisador pode ser executado mesmo antes da implementacao do gerador:

```powershell
docker compose run --rm --entrypoint python maze maze_analyzer.py maze.txt
```

Substitua `maze.txt` pelo caminho de um arquivo de labirinto existente no projeto.

## Abrir um shell no container

```powershell
docker compose run --rm --entrypoint sh maze
```
