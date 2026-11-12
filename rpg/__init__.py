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

Example:
    >>> from rpg import Guerreiro, Caverna, Combate
    >>> resultado = Combate(Guerreiro("Aragorn"), Guerreiro("Boromir"), Caverna()).executar()
    >>> resultado.vencedor.nome
    'Aragorn'
"""

from rpg.aldeao import Aldeao
from rpg.cenario import Castelo, Caverna, Cenario, Floresta, criar_cenario
from rpg.combate import Combate, RegistroTurno, ResultadoCombate
from rpg.excecoes import (
    AlvoInvalidoError,
    CenarioInvalidoError,
    CombateInfinitoError,
    DanoInvalidoError,
    GrupoCheioError,
    ItemNaoEncontradoError,
    PersonagemMortoError,
    RPGError,
    SemManaError,
    ValorInvalidoError,
    VidaInvalidaError,
)
from rpg.ficha import FichaDeStatus
from rpg.grupo import Grupo
from rpg.interfaces import Combatente
from rpg.inventario import Inventario
from rpg.itens import Arma, Armadura, Item, Pocao
from rpg.personagem import Arqueiro, Guerreiro, Mago, Personagem

__all__ = [
    "Aldeao",
    "Arma",
    "Armadura",
    "AlvoInvalidoError",
    "Arqueiro",
    "Castelo",
    "Caverna",
    "Cenario",
    "CenarioInvalidoError",
    "Combate",
    "CombateInfinitoError",
    "Combatente",
    "DanoInvalidoError",
    "FichaDeStatus",
    "Floresta",
    "Grupo",
    "GrupoCheioError",
    "Guerreiro",
    "Inventario",
    "Item",
    "ItemNaoEncontradoError",
    "Mago",
    "Personagem",
    "PersonagemMortoError",
    "Pocao",
    "RPGError",
    "RegistroTurno",
    "ResultadoCombate",
    "SemManaError",
    "ValorInvalidoError",
    "VidaInvalidaError",
    "criar_cenario",
]
