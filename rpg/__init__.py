"""Sistema de RPG em console — domínio orientado a objetos.

Pacote com a modelagem completa do trabalho de POO:

* :mod:`rpg.excecoes` — erros de domínio
* :mod:`rpg.interfaces` — contrato ``Combatente``
* :mod:`rpg.itens` — ``Item`` abstrata e subclasses
* :mod:`rpg.ficha` — composição ``FichaDeStatus``
* :mod:`rpg.inventario` — composição ``Inventario``
* :mod:`rpg.personagem` — ``Personagem`` abstrata e subclasses
* :mod:`rpg.aldeao` — objeto que não é combatente
* :mod:`rpg.grupo` — agregação
* :mod:`rpg.cenario` — ambiente que favorece o usuário
* :mod:`rpg.combate` — orquestração (consumo de classe)
* :mod:`rpg.cli` — menu de console
"""
