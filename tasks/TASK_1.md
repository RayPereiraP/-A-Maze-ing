Task
Objective

Implementar duas classes, Celula e Mapa, que representam um labirinto em grade. A célula guarda apenas o estado das próprias paredes. O mapa guarda a grade e é o único que conhece posições e vizinhanças.

Context
O labirinto é uma grade 2D de células.
Cada célula tem quatro paredes (N, S, E, W) e uma marcação de caminho.
A posição de uma célula na grade é conhecida só pelo Mapa. A Celula não sabe onde está.
Abrir uma parede entre duas células vizinhas exige alterar as duas células. Só o Mapa sabe quem é o vizinho.
Instructions
Inspecionar o projeto para identificar a linguagem, a estrutura de pastas e as convenções existentes. Se o projeto estiver vazio, seguir as Open Questions abaixo.
Criar a classe Celula com:
quatro booleanos, um por parede (N, S, E, W), onde true é parede e false é caminho livre;
um booleano indicando se a célula faz parte do caminho;
valores iniciais: as quatro paredes como true (fechadas) e o indicador de caminho como false.
Garantir que Celula não tenha coordenadas, referência ao Mapa nem referência a outras células.
Criar a classe Mapa com:
uma estrutura de array de arrays (matriz) contendo todas as Celula;
um construtor que recebe as dimensões (linhas e colunas) e preenche a matriz com células novas.
Implementar no Mapa a operação de abrir parede, dada uma célula (por posição) e uma direção:
definir como false a parede da célula de origem na direção indicada;
calcular a posição do vizinho naquela direção;
definir como false a parede oposta da célula vizinha (N↔S, E↔W).
Tratar no Mapa o caso de abrir parede em direção a fora da grade (borda), rejeitando a operação ou ignorando-a, sem alterar nenhuma célula.
Expor no Mapa um meio de acessar uma célula por posição, para permitir verificação do estado.
Constraints
A Celula só conhece suas quatro paredes e o indicador de caminho.
Toda lógica de posição, vizinhança e direção oposta fica no Mapa.
Usar array de arrays para armazenar as células, sem outra estrutura de dados para a grade.
Não adicionar funcionalidades além das descritas, como geração de labirinto, busca de caminho ou renderização.
Não adicionar dependências externas.
Acceptance Criteria
Uma Celula recém-criada tem N, S, E e W como true e o indicador de caminho como false.
A Celula não possui atributo ou método que dependa de posição.
Um Mapa criado com R linhas e C colunas contém R×C células, em R arrays de C elementos.
Abrir a parede leste de (r, c) deixa a parede E de (r, c) e a parede W de (r, c+1) como false. O mesmo vale, com os pares correspondentes, para as outras direções.
Abrir uma parede não altera as outras três paredes de nenhuma das duas células.
Validation
Escrever e executar testes cobrindo o estado inicial da célula, as dimensões do mapa, a abertura de parede nas quatro direções e a abertura em direção à borda.
Conferir que a abertura de uma parede altera exatamente as duas paredes esperadas e mais nenhuma.
Se o projeto já tiver testes, rodar os existentes para garantir que não houve regressão.
Open Questions
Em qual linguagem as classes devem ser implementadas? Não foi informada e não há projeto existente para inferir.