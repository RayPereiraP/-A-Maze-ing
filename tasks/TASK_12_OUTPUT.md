# Task 12 — Output

Implementação da Task 12 do [TASKS.md](TASKS.md): o `LICENSE.md` na raiz do repositório, com uma licença que permite reuso e distribuição do gerador. Não havia um `TASK_12.md`, então segui o `TASKS.md` e o capítulo VI do subject. O `TASKS.md` não foi alterado.

## Resultado

- [LICENSE.md](../LICENSE.md) está na raiz, com a licença **MIT**.
- O pacote `mazegen` foi reconstruído e agora leva a licença dentro dele.
- Os 96 testes continuam passando; `flake8 .` e `mypy . --strict` continuam limpos.

A escolha da licença é uma decisão tua: o subject diz que escolher e escrever a licença faz parte do trabalho, e o `TASKS.md` só considera a task pronta quando souberes explicar a escolha. Escolhi a MIT como proposta e explico abaixo o porquê e as alternativas. Se preferires outra, é trocar um arquivo e duas linhas.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `LICENSE.md` | novo: o texto da licença MIT |
| `pyproject.toml` | `license = "MIT"` e `license-files = ["LICENSE.md"]`; `setuptools>=77` |
| `src/mazegen/README.md` | nova seção "License" no fim |
| `mazegen-1.0.0-py3-none-any.whl`, `mazegen-1.0.0.tar.gz` | reconstruídos, com a licença dentro |

## O que o subject pede

> you must include a LICENSE.md file at the root of your repository, stating the license under which your code may be reused. [...] The license you pick must explicitly allow the reuse and distribution of your maze generator by the later project(s) that build on it.

Três exigências: o arquivo chama-se `LICENSE.md`, está na raiz, e a licença permite **explicitamente** reuso e distribuição.

## Por que uma licença é necessária

Sem licença nenhuma, o código não é "livre": por padrão, o direito de autor reserva tudo a quem escreveu. Estar público num repositório deixa as pessoas **ler** o código, mas não lhes dá o direito de copiar, modificar ou distribuir. A licença é o documento em que o autor dá essas permissões, e diz em que condições.

## A licença MIT, parte por parte

O texto tem três parágrafos.

**1. A permissão.**

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software [...] to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software

Qualquer pessoa pode usar, copiar, modificar, juntar com outro código, publicar, distribuir, sublicenciar e vender. É aqui que está o "explicitly allow the reuse and distribution" do subject: as palavras *use*, *copy* e *distribute* aparecem escritas.

**2. A única condição.**

> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

Quem copiar o código tem de manter a linha de copyright e o texto da licença. Só isso. Não precisa abrir o código do projeto que o usa, nem pedir autorização.

**3. A isenção de garantia.**

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND [...]

O código é entregue como está. Se tiver um bug e causar um prejuízo, o autor não é responsável. As maiúsculas são tradição jurídica americana: a isenção tem de ser "bem visível".

## Por que MIT e não outra

| Licença | O que permite | Condição principal | Para este projeto |
|---------|---------------|--------------------|-------------------|
| **MIT** | usar, copiar, modificar, distribuir, vender | manter o copyright e o texto | curta, dá para ler e explicar inteira |
| BSD 3-Clause | o mesmo | o mesmo, mais: não usar o nome do autor para promover derivados | equivalente; uma cláusula a mais sem utilidade aqui |
| Apache 2.0 | o mesmo | manter avisos e indicar o que foi alterado; trata de patentes | texto longo (cerca de 200 linhas); pensada para projetos com empresas e patentes |
| GPL v3 | o mesmo | quem distribuir um programa que use o código tem de o distribuir também sob GPL, com as fontes | obrigaria os projetos futuros que usarem o `mazegen` a serem GPL |
| Sem licença | nada | — | não cumpre o subject |

Os motivos da escolha:

- **Cumpre o subject pela letra:** a permissão de usar e distribuir está escrita no primeiro parágrafo.
- **Não impõe nada ao projeto futuro.** O subject diz que o `mazegen` vai ser reutilizado por projeto(s) posteriores. Com a MIT, esse projeto pode ter a licença que quiser. Com a GPL, teria de ser GPL também.
- **É curta.** São 21 linhas. Numa avaliação, consegues ler e explicar cada parágrafo, o que seria difícil com a Apache ou a GPL.
- **É a mais comum** em bibliotecas Python pequenas.

O que se perde com a MIT: alguém pode pegar no código, melhorá-lo e não publicar as melhorias. Se isso te incomodar, a escolha coerente seria a GPL, com o custo descrito na tabela.

## A linha de copyright

```
Copyright (c) 2026 Mateus
```

- **2026** é o ano em que o código foi escrito.
- **Mateus** é o nome configurado no teu git. Convém pôr o teu nome completo, ou o teu login da 42: é a linha que identifica o titular dos direitos.

## A licença dentro do pacote

A condição da MIT é que o texto acompanhe as cópias. O `.whl` é uma cópia do código, então a licença tem de estar lá dentro. Duas linhas no `pyproject.toml`:

```toml
license = "MIT"
license-files = ["LICENSE.md"]
```

- `license` é o identificador padrão (SPDX) da licença; aparece em `pip show mazegen`.
- `license-files` diz que arquivo copiar para dentro do pacote.

Esta forma de escrever a licença só existe a partir do `setuptools` 77, por isso o `requires` passou de `setuptools>=61` para `setuptools>=77`. Isso não exige nada de quem instala: o `build` baixa o `setuptools` certo sozinho, num ambiente isolado.

Depois do rebuild, conferi:

| Onde | O que há |
|------|----------|
| `.whl` | `mazegen-1.0.0.dist-info/licenses/LICENSE.md` |
| `.tar.gz` | `mazegen-1.0.0/LICENSE.md` |
| `METADATA` | `License-Expression: MIT` e `License-File: LICENSE.md` |
| `pip show mazegen` | `License-Expression: MIT` |

Os dois arquivos, reconstruídos, foram instalados de novo em virtualenvs limpos e importados, como na Task 11.

## Decisões que tomei

- **MIT**, pelos motivos acima.
- **O texto é o oficial, sem alterações**, com um título `# MIT License` por ser um arquivo Markdown. Uma licença conhecida só vale como "MIT" se o texto for o original.
- **Em inglês.** É a língua do texto oficial; uma tradução não seria a licença MIT.
- **Uma licença para o repositório inteiro**, não só para o `mazegen`. O subject fala do gerador, mas um único `LICENSE.md` na raiz cobre tudo e evita ter duas regras.
- **Reconstruí o pacote** e substituí os dois arquivos da raiz, para a licença ir dentro deles.
- **Acrescentei uma seção "License" ao README do módulo**, de três linhas, para quem instalar o pacote saber as regras sem abrir o arquivo.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "o arquivo está na raiz e você sabe explicar a escolha".

| Critério | Estado |
|----------|--------|
| O arquivo está na raiz | feito: `LICENSE.md` |
| Permite reuso e distribuição, explicitamente | feito: primeiro parágrafo da MIT |
| Saber explicar a escolha | depende de ti; as seções "parte por parte" e "Por que MIT e não outra" são o material |

## Pontos de atenção

- **O nome no copyright é só "Mateus".** Troca pelo nome completo ou pelo login, e reconstrói o pacote depois (`make build`), porque o `.whl` leva uma cópia do arquivo.
- **`42_M02_A-Maze-Ing-main/` não é código teu.** O `LICENSE.md` da raiz diz "Copyright Mateus" sobre o repositório, mas essa pasta é um projeto de outra pessoa. Uma licença só pode ser dada por quem é o autor. É mais um motivo para decidir se essa pasta deve ficar no repositório da entrega.
- **O `maze_analyzer.py` e o `en.subject.pdf` vieram da 42**, pelo mesmo raciocínio: não são cobertos pela tua licença.
- **O `README.md` principal ainda não menciona a licença.** Fica para a Task 13.
- **Não sou advogado.** A explicação acima é a leitura corrente da licença MIT, suficiente para a avaliação; não é aconselhamento jurídico.
- **Os dois arquivos `mazegen-*` mudaram** e continuam sem commit, como o resto.
