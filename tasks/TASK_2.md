Task: Adicionar padrão "42" central ao labirinto via Cell.is_42 e Map.__init__
Objective

Adicionar a propriedade booleana is_42 à classe Cell e fazer com que o construtor da classe Map marque, ao final de sua inicialização, as células que formam o desenho do número "42" no centro do labirinto. Se o desenho não puder ser aplicado, ele deve ser omitido com uma mensagem de erro no console.

Context
O projeto contém as classes Cell e Map (labirinto). Os arquivos e a linguagem não foram informados; devem ser descobertos por inspeção.
Map.__init__ já executa uma sequência de etapas (as "linhas atuais") que constroem o labirinto.
Uma célula é considerada parte do "42" se, e somente se, cell.is_42 for True.
O labirinto tem uma entrada e uma saída.
Instructions
Inspecione o projeto e localize as classes Cell e Map, a forma como Map.__init__ constrói o labirinto, a estrutura de armazenamento das células e a representação da entrada e da saída.
Na classe Cell, adicione a propriedade is_42 do tipo booleano, com valor inicial False, seguindo as convenções de declaração de atributos já usadas na classe.
Em Map.__init__, após o término das etapas atuais, adicione uma etapa final que percorre as células do labirinto e marca is_42 = True nas células que formam o desenho do número "42", posicionado no centro do labirinto.
Antes de marcar qualquer célula, verifique as duas condições de omissão:
O labirinto é pequeno demais para comportar o desenho do "42" centralizado.
A entrada ou a saída coincide com alguma célula que seria marcada como parte do desenho.
Se qualquer uma das condições for verdadeira, não marque nenhuma célula (is_42 permanece False em todas), omita o padrão e exiba uma mensagem de erro no console indicando o motivo (labirinto pequeno demais ou entrada/saída sobre o desenho).
Garanta que o restante do código que precisar saber se uma célula pertence ao "42" use exclusivamente cell.is_42, sem outro mecanismo paralelo.
Constraints
Não altere o comportamento atual das etapas já existentes em Map.__init__; a nova etapa vem somente ao final delas.
A marcação do padrão deve ocorrer dentro de __init__, não em um método chamado externamente.
A omissão do padrão não deve interromper a execução nem lançar exceção; apenas exibe a mensagem de erro no console e prossegue.
A omissão é total: o desenho nunca é aplicado parcialmente.
Não invente novos requisitos, dependências ou refatorações em código não relacionado.
O dimensionamento exato do desenho "42" (altura e largura em células) não foi especificado; escolha um tamanho mínimo razoável e mantenha-o definido em um único lugar do código.
Acceptance Criteria
Cell possui a propriedade booleana is_42, com valor padrão False.
Em um labirinto grande o suficiente e sem sobreposição com a entrada/saída, as células centrais que formam o "42" têm is_42 == True, e todas as demais têm is_42 == False.
Em um labirinto pequeno demais, nenhuma célula tem is_42 == True e uma mensagem de erro é exibida no console.
Quando a entrada ou a saída cai sobre o desenho, nenhuma célula tem is_42 == True e uma mensagem de erro é exibida no console.
O comportamento anterior da construção do labirinto permanece inalterado fora do padrão "42".
Validation
Execute os testes existentes do projeto relevantes para Cell e Map e confirme que continuam passando.
Construa um labirinto grande o suficiente e verifique que as células marcadas formam o "42" centralizado.
Construa um labirinto pequeno demais e verifique a ausência de células com is_42 == True e a presença da mensagem de erro no console.
Construa um labirinto em que a entrada ou a saída coincida com uma célula do desenho e verifique o mesmo comportamento de omissão com mensagem de erro.