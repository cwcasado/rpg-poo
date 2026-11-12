Crie um sistema de RPG que considere todos os pontos usados até o momento dentro do sistema de POO usado nessa aula.

Preciso de:

Caso de Uso
Visão de Projeto
Diagrama de Classe
O sistema precisa considerar e conter todos os conceitos de POO usados até esse momento em sala de aula, contidos no link de https://diegorinacio.github.io/POO/.

Configurações necessárias do sistema
O modelo (Visão de Projeto + Diagrama de Classe) precisa deixar explícitas as regras de cada aula, aplicadas ao domínio do RPG:

Classes e Objetos — personagens, itens e cenários modelados como classes, instanciados como objetos (ex.: Personagem, Item, Cenario).
Atributos, Métodos e Interação — cada classe com seus atributos de estado (vida, força, defesa) e métodos de ação (atacar, defender, usar item) que fazem os objetos interagirem entre si.
Abstração — pelo menos uma classe abstrata que não pode ser instanciada diretamente (ex.: Personagem abstrato, só suas subclasses existem de fato).
Interface — pelo menos um contrato obrigatório (ex.: Combatente com o método atacar()), que só quem implementa pode participar de um combate.
Herança — uma hierarquia de personagens (ex.: Guerreiro, Mago, Arqueiro herdando de Personagem), cada um com seu próprio comportamento.
Tratamento de Exceções — erros próprios do domínio (ex.: dano inválido, vida que não pode ficar negativa, item inexistente no inventário).
Agregação — relação explícita no diagrama: um objeto que existe fora de outro e é associado a ele (ex.: Personagem cadastrado em um Grupo/Guilda, que continua existindo mesmo se o grupo acabar).
Composição — relação explícita no diagrama: um objeto que nasce junto com outro e não existe fora dele (ex.: o Inventario ou a FichaDeStatus que nasce junto com o Personagem).
Consumo de classe — no diagrama e na visão de projeto, deixar claro quais classes dependem/usam os métodos de quais outras (ex.: o Cenario consome Personagem.atacar(), o Combate consome Personagem e Item) — essa relação de uso entre classes precisa estar documentada, não só implícita no código.
Ambiente que favorece o usuário
O sistema precisa ter um ambiente/cenário (ex.: Floresta, Caverna, Castelo) que concede vantagem a determinado tipo de personagem (ex.: a Floresta favorece o Arqueiro, a Caverna favorece o Guerreiro) — isso deve aparecer como uma regra de negócio clara no Caso de Uso e refletida nas classes do diagrama.

Sem parte gráfica
Não é permitido back-end (nenhuma API, rota HTTP, servidor) nem front-end (nenhuma interface gráfica, HTML ou tela). O sistema roda inteiramente via código/console.

Precisando de alguma coisa, estou à disposição para tirar quaisquer dúvidas referente ao assunto.