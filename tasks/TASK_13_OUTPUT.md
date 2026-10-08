# Task 13 — Output

Implementação da Task 13 do [TASKS.md](TASKS.md): o `README.md` da raiz. Não havia um `TASK_13.md`, então segui o `TASKS.md` e os capítulos VI e VII do subject. O `TASKS.md` não foi alterado.

## Resultado

- [README.md](../README.md) reescrito, em inglês, com todas as seções que o subject exige.
- **Não está pronto para entregar:** há três coisas que só tu podes preencher ou confirmar. Estão na seção "O que precisa de ti", logo abaixo.
- Os cinco blocos de código Python do README foram executados e funcionam; os links internos apontam para arquivos que existem.
- Nenhum arquivo de código foi alterado; os 96 testes continuam passando.

## O que precisa de ti

1. **O teu login da 42.** Aparece como `LOGIN_HERE` em dois lugares: na primeira linha e na tabela "Team". Não o encontrei em lugar nenhum do repositório.
2. **A equipe.** Escrevi como projeto de uma pessoa só. O git tem dois commits de outra autora (Rayane), ambos só no README antigo. Se ela faz parte da equipe, a primeira linha e a tabela de papéis têm de incluí-la.
3. **A seção "How AI was used".** É a tua declaração perante os avaliadores, e o subject pede que diga para que tarefas e em que partes a IA foi usada. O que escrevi está descrito mais abaixo, com o que sei e o que não sei. Lê e corrige para ficar igual ao que aconteceu.

Também convém releres "What worked well" e "What could be improved": são reflexões, e escrevi-as a partir do que está nos relatórios das tasks, não da tua experiência.

## Arquivos

| Arquivo | O que mudou |
|---------|-------------|
| `README.md` | reescrito por inteiro |

O README antigo tinha mensagens pessoais e uma tabela dos bits das paredes. Foi substituído. A versão antiga continua no histórico do git (`git show HEAD:README.md`). A tabela dos bits foi mantida, na seção "Output file".

## O que o subject exige e onde está

| Exigência (capítulo VII) | Seção do README |
|--------------------------|-----------------|
| Primeira linha em itálico, com o texto exato e os logins | linha 1 |
| "Description": objetivo e visão geral | Description |
| "Instructions": instalação e execução | Instructions |
| "Resources": referências e uso de IA | Resources |
| Estrutura e formato completos do config | Configuration file |
| O algoritmo escolhido | The maze generation algorithm |
| Por que esse algoritmo | Why this algorithm |
| Que parte do código é reutilizável, e como | Reusable code: the `mazegen` package |
| Papéis de cada membro | Team |
| Planejamento previsto e como evoluiu | Planning |
| O que funcionou e o que melhorar | What worked well / What could be improved |
| Ferramentas usadas | Tools |

E do capítulo VI: "The main README.md file must also contain this short documentation" — a documentação do `mazegen` (instanciar, parâmetros, estrutura, solução) está repetida na seção do pacote, com o mesmo conteúdo de `src/mazegen/README.md`.

Não há seção de funcionalidades avançadas: só a parte mandatória foi feita, e o README diz isso.

## A primeira linha

```markdown
*This project has been created as part of the 42 curriculum by LOGIN_HERE.*
```

O subject pede que seja a **primeiríssima** linha e em itálico; em Markdown, itálico é o texto entre asteriscos. O título `# A-Maze-ing` vem depois dela, não antes. Com dois autores, o formato é `by login1, login2.`

Usei `LOGIN_HERE` e não `<login>` de propósito: o Markdown trataria `<login>` como uma tag HTML e a palavra sumiria na página.

## De onde veio cada informação

Tudo o que o README afirma sobre o programa foi tirado do código, não de memória:

| Seção | Fonte |
|-------|-------|
| Formato do config | `src/parser.py`: chaves obrigatórias, `SEED` opcional, linhas em branco e `#` ignoradas, chave repetida recusada, chaves desconhecidas aceitas |
| Arquivo de saída | `src/mazegen/writer.py` |
| Algoritmo | `src/mazegen/generator.py`: `generate_perfect` e `open_loops` |
| Caminho mais curto | `src/mazegen/solver.py` |
| Menu e símbolos | `src/main.py` e `src/renderer.py` |
| Regras do Makefile | `Makefile` |
| Documentação do `mazegen` | `src/mazegen/README.md`, já testada na Task 11 |

O desenho de exemplo da seção "Run" é uma saída real do programa: 5x3, `PERFECT=False`, `SEED=3`, com o caminho ligado.

## O algoritmo, como está explicado

O README descreve três coisas, na ordem em que o código as faz:

1. **Labirinto perfeito:** busca em profundidade com retrocesso (*recursive backtracker*). Anda para um vizinho nunca visitado, abrindo a parede; sem vizinho livre, volta um passo.
2. **Tabuleiro com loops:** parte do perfeito e abre paredes a mais, se ainda faltam loops ou se uma das células é dead-end, e nunca se isso formar uma área aberta 3x3.
3. **Caminho mais curto:** busca em largura.

Os motivos da escolha, que são o que te podem perguntar na avaliação:

- **É correto por construção.** Só se abre parede para uma célula nunca visitada, logo não nasce loop; e a busca só acaba depois de alcançar todas as células.
- **É simples:** uma pilha e um conjunto de visitados.
- **É reproduzível:** todo o acaso vem de um único `random.Random(seed)`.
- **Dá corredores longos e sinuosos.**
- **É rápido:** cada célula entra e sai da pilha uma vez.

E o custo, dito no README: corredores longos e poucas bifurcações. Prim e Kruskal dão mais becos curtos, mas pedem mais estrutura (lista de fronteira, ou union-find).

O README também explica por que a pilha é uma lista e não chamadas recursivas: um labirinto grande estouraria o limite de recursão do Python.

## A seção "How AI was used"

O que escrevi diz que um assistente de IA (Claude Code) foi usado task por task, para:

- escrever a primeira versão do código e dos testes de cada task;
- escrever o relatório de cada task (`tasks/TASK_N_OUTPUT.md`), usado para estudar cada parte;
- a parte de entrega: Makefile, configuração do lint, empacotamento, proposta de licença e o rascunho do próprio README.

E que ficou contigo: decidir a ordem e o limite de cada task, aceitar ou devolver cada resultado, escolher a licença e só marcar uma task como pronta depois de a entender.

O que sei e o que não sei:

- **Sei** das Tasks 9 a 13, feitas nesta conversa: o código, os testes e os relatórios foram escritos por mim.
- **Não sei** como foram as Tasks 0 a 8. Existem relatórios no mesmo formato, mas não participei delas. Se usaste outra ferramenta, ou se escreveste partes à mão, o texto tem de dizer isso.
- **Não sei** quem dividiu o subject nas tasks do `TASKS.md`, por isso não atribuí o planejamento à IA.

O capítulo II do subject é explícito: só se deve usar conteúdo gerado por IA que se entende por completo, e na avaliação podem pedir para explicar ou alterar qualquer parte. Uma declaração honesta aqui é o que te protege; uma que diminua o uso real é um risco.

## Decisões que tomei

- **Em inglês.** O subject recomenda, e o código já está em inglês.
- **A documentação do `mazegen` foi copiada, não só linkada.** O subject pede que o README principal "contenha" a documentação.
- **Incluí uma seção "Output file"** com a tabela dos bits. Não é exigida, mas ajuda quem lê o arquivo de saída, e preserva a tabela do README antigo.
- **Incluí uma tabela "Project structure".** Também não é exigida; serve para quem chega ao repositório sem contexto.
- **Não mencionei o Docker nas instruções de uso.** O `DOCKER.md` existe, mas está em português e diz que o `a_maze_ing.py` "ainda precisa" de ser feito, o que já não é verdade. O Docker aparece só em "Tools", que é como foi usado nas Tasks 10 a 12.
- **As referências são clássicas e verificáveis:** o artigo e o livro de Jamis Buck sobre geração de labirintos, as páginas da Wikipedia dos algoritmos, e a documentação oficial das ferramentas usadas.
- **"What could be improved" lista limitações reais**, tiradas dos "Pontos de atenção" das Tasks 8 a 11: largura do terminal, caminho sem direção, o aviso do "42" impresso pela biblioteca, e o Makefile testado só em container.

## Critérios de aceitação

O `TASKS.md` define a task como pronta quando "alguém de fora consegue rodar o projeto e usar o módulo só lendo o README".

| Critério | Como verifiquei |
|----------|-----------------|
| Rodar o projeto só com o README | os comandos de "Install" e "Run" são os que rodei no container nas Tasks 10 e 11 |
| Usar o módulo só com o README | os cinco blocos Python do README foram extraídos e executados em sequência, sem erro |
| Links internos | `config.txt`, `src/mazegen/`, `LICENSE.md` e `tasks/TASKS.md` existem |
| Primeira linha | é a linha 1, em itálico, com o texto do subject; falta o login |

O que **não** verifiquei: os links externos das referências não foram abertos; e ninguém "de fora" leu o README, que é o teste de verdade deste critério.

## Pontos de atenção

- **`LOGIN_HERE` aparece duas vezes.** Procura por essa palavra antes de entregar.
- **Executar os exemplos do README reescreveu o `maze.txt`**, porque um deles é `generator.write("maze.txt")`. Rodei o programa de novo com o `config.txt` para o `maze.txt` voltar a corresponder ao config (10x10, seed 1).
- **O `DOCKER.md` está desatualizado**, como dito acima. Não mexi nele.
- **Pendências das tasks anteriores que afetam a entrega**, todas ainda em aberto:
  - a pasta `42_M02_A-Maze-Ing-main/` (projeto de outra pessoa) continua versionada;
  - o copyright do `LICENSE.md` diz só "Mateus";
  - nada foi commitado desde a Task 8, incluindo os dois arquivos `mazegen-*` que o subject exige na raiz.
- **Se mudares o `src/mazegen/README.md`, muda também a seção do pacote no README principal** (e vice-versa): são duas cópias do mesmo texto.
