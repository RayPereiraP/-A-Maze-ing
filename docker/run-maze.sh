#!/bin/sh
set -eu

if [ ! -f /app/a_maze_ing.py ]; then
    printf '%s\n' 'Erro: a_maze_ing.py ainda nao existe no projeto.' 'Este container executa o gerador; maze_analyzer.py apenas analisa arquivos de labirinto.' >&2
    exit 1
fi

if [ "$#" -eq 0 ]; then
    set -- config.txt
fi

if [ "$#" -ne 1 ]; then
    printf '%s\n' 'Uso: docker compose run --rm maze <arquivo-de-configuracao>' >&2
    exit 1
fi

if [ ! -f "$1" ]; then
    printf 'Erro: arquivo de configuracao nao encontrado: %s\n' "$1" >&2
    exit 1
fi

exec python /app/a_maze_ing.py "$1"
